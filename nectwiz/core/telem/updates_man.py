import time
from datetime import datetime
from functools import wraps
from typing import Dict, List, Optional

from nectwiz.core.core import utils, hub_client
from nectwiz.core.core.config_man import config_man
from nectwiz.core.core.types import UpdateDict, UpdateOutcome, ActionOutcome
from nectwiz.core.core.utils import dict2keyed
from nectwiz.core.tam.tam_provider import tam_client
from nectwiz.core.telem.update_observer import UpdateObserver
from nectwiz.model.chart_variable.chart_variable import ChartVariable
from nectwiz.model.hook.hook import Hook
from nectwiz.model.predicate import default_predicates
from nectwiz.model.step import status_computer
from nectwiz.model.step.step_state import StepState

TYPE_RELEASE = 'release'
TYPE_UPDATE = 'update'

def raise_on_false(f):
  @wraps(f)
  def wrapper(*args, **kwargs):
    result = f(*args, **kwargs)
    if not result:
      raise HaltedError("step returned false")
    return result
  return wrapper


def fetch_next_update() -> Optional[UpdateDict]:
  config_man.write_last_update_checked(str(datetime.now()))
  return None


def next_available() -> Optional[UpdateDict]:
  uuid = config_man.install_uuid()
  url = f'/api/cli/{uuid}/app_updates/available'
  resp = hub_client.get(url)
  data = resp.json()['data'] if resp.status_code < 205 else None
  print(f"[nw::updates_man] avail: {data}")
  return data['bundle'] if data else None


def install_update(update: UpdateDict, observer=None) -> UpdateOutcome:
  observer = observer or UpdateObserver(update.get('type'))
  pre_op_tam = config_man.mfst_vars(True)

  try:
    run_hooks('before', update, observer)
    perform(update, observer)
    await_resource_settled(observer)
    run_hooks('after', update, observer)
    notify_checked()
    observer.on_succeeded()
  except HaltedError:
    print("Early stop!")

  return UpdateOutcome(
    update_id=update.get('id'),
    type=update.get('type'),
    version=update.get('version'),
    apply_logs=observer.get_ktl_apply_logs(),
    pre_man_vars=pre_op_tam,
    post_man_vars=config_man.mfst_vars(True)
  )

@raise_on_false
def perform(update: UpdateDict, observer: UpdateObserver) -> bool:
  observer.on_perform_started()

  _type = update.get('type')
  if _type == TYPE_RELEASE:
    log_chunk = apply_release(update, observer)
  elif _type == TYPE_UPDATE:
    log_chunk = apply_update(update)
  else:
    print(f"[nectwiz::updates_man] illegal update type '{_type}'!")
    return False

  observer.on_perform_finished('positive', log_chunk)
  return True

@raise_on_false
def run_hooks(which, update: UpdateDict, observer: UpdateObserver) -> bool:
  hooks = Hook.by_trigger(
    event='software-update',
    update_type=update['type'],
    timing=which,
  )

  observer.on_hook_set_started(which, [hook.title for hook in hooks])
  for hook in hooks:
    outcome: ActionOutcome = hook.run()
    charge: str = outcome['charge']
    observer.on_hook_done(which, hook.title, charge)
    if charge == 'negative' and hook.abort_on_fail:
      observer.on_hook_set_done(which)
      observer.on_fatal_error()
      return False

  observer.on_hook_set_done(which)
  return True


@raise_on_false
def apply_release(release: UpdateDict, observer: UpdateObserver) -> str:
  config_man.patch_tam(dict(version=release['version']))
  target_var_ids = [cv.id() for cv in ChartVariable.release_dpdt_vars()]
  new_mfst_defaults = tam_client().load_manifest_defaults()
  new_keyed_defaults = dict2keyed(new_mfst_defaults)
  overridden_vars = [e for e in new_keyed_defaults if e[0] in target_var_ids]
  config_man.commit_keyed_mfst_vars(overridden_vars)
  observer.on_mfst_vars_committed(overridden_vars)
  config_man.write_mfst_defaults(new_mfst_defaults)
  return tam_client().apply([])


@raise_on_false
def await_resource_settled(observer: UpdateObserver) -> bool:
  logs = observer.get_ktl_apply_logs()
  predicate_tree = default_predicates.from_apply_outcome(logs)
  predicates = utils.flatten(predicate_tree.values())
  state = StepState('synthetic', None)
  for i in range(120):
    status_computer.compute(predicate_tree, state)
    observer.on_exit_statuses_computed(predicates, state.exit_statuses)
    if state.has_settled():
      break
    else:
      time.sleep(2)

  observer.on_settled(state.status)
  return state.did_succeed()


@raise_on_false
def apply_update(patch: UpdateDict) -> str:
  keyed_or_nested_asgs: Dict = patch.get('injections', {})
  keyed = utils.dict2keyed(keyed_or_nested_asgs)
  config_man.commit_keyed_mfst_vars(keyed)
  return tam_client().apply([])


@raise_on_false
def notify_checked() -> bool:
  uuid = config_man.install_uuid()
  url = f'/api/cli/{uuid}/app_updates/notify_checked_update'
  resp = hub_client.post(url, dict(data=dict(
    tam_type=config_man.tam().get('type'),
    tam_uri=config_man.tam().get('uri'),
    tam_version=config_man.tam().get('version'),
  )))
  print(f"[updates_man::notify_checked] resp: {resp}")
  return resp.status_code < 205


def _gen_injection_telem(keys: List[str]):
  all_vars = config_man.read_mfst_vars()
  return {k: all_vars[k] for k in keys}


class HaltedError(RuntimeError):
  pass
