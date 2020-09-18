from typing import Dict, List, Optional, TypedDict

from nectwiz.core.core import utils, hub_client
from nectwiz.core.core.utils import dict2keyed

from nectwiz.core.core.config_man import config_man
from nectwiz.core.tam.tam_provider import tam_client
from nectwiz.core.core.types import UpdateDict, UpdateOutcome, ActionOutcome
from datetime import datetime

from nectwiz.core.telem.update_observer import UpdateObserver
from nectwiz.model.chart_variable.chart_variable import ChartVariable
from nectwiz.model.hook.hook import Hook

TYPE_RELEASE = 'release'
TYPE_UPDATE = 'update'


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


def notify_checked() -> bool:
  uuid = config_man.install_uuid()
  url = f'/api/cli/{uuid}/app_updates/notify_checked_update'
  resp = hub_client.post(url, dict(data=dict(
    tam_type=config_man.tam().get('type'),
    tam_uri=config_man.tam().get('uri'),
    tam_version=config_man.tam().get('version'),
  )))
  print(f"[nw::updates_man] notif checked: {resp}")
  return resp.status_code < 205


def perform_update(update: UpdateDict) -> UpdateOutcome:
  observer = UpdateObserver()
  pre_op_tam = config_man.mfst_vars(True)

  run_hooks('before', update, observer)
  replace_resources(update, observer)
  run_hooks('after', update, observer)
  notify_checked()
  observer.on_succeeded()

  return UpdateOutcome(
    update_id=update.get('id'),
    type=update.get('type'),
    version=update.get('version'),
    apply_logs=observer.progress['perform_progress']['logs'],
    pre_man_vars=pre_op_tam,
    post_man_vars=config_man.mfst_vars(True)
  )


def replace_resources(update: UpdateDict, observer: UpdateObserver):
  _type = update.get('type')
  if _type == TYPE_RELEASE:
    log_chunk = apply_upgrade(update)
  elif _type == TYPE_UPDATE:
    log_chunk = apply_update(update)
  else:
    raise RuntimeError(f"[nectwiz::updates_man] illegal update type '{_type}'")

  post_op_tam = config_man.mfst_vars(True)
  log_lines = log_chunk.split("\n") if log_chunk else []
  res_effects = list(map(utils.log2ktlapplyoutcome, log_lines))




def run_hooks(timing, update: UpdateDict, observer: UpdateObserver) -> bool:
  hooks = Hook.by_trigger(
    event='software-update',
    update_type=update['type'],
    timing=timing,
  )

  observer.on_hook_set_started(timing, [hook.title() for hook in hooks])
  for hook in hooks:
    outcome: ActionOutcome = hook.action().run()
    charge: str = outcome['charge']
    message: str = (outcome.get('data') or {}).get('message') or ''

    observer.on_hook_done(timing, hook.title, charge, message)
    if charge == 'negative' and hook.abort_on_fail:
      observer.on_fatal_error()
      return False

  return True



def run_post_hooks(update: UpdateDict):
  pass


def apply_upgrade(release: UpdateDict) -> str:
  config_man.patch_tam(dict(version=release['version']))
  target_var_ids = [cv.id() for cv in ChartVariable.release_dpdt_vars()]
  new_mfst_defaults = tam_client().load_manifest_defaults()
  new_keyed_defaults = dict2keyed(new_mfst_defaults)
  overridden_vars = [e for e in new_keyed_defaults if e[0] in target_var_ids]
  config_man.commit_keyed_mfst_vars(overridden_vars)
  config_man.write_mfst_defaults(new_mfst_defaults)
  return tam_client().apply([])


def apply_update(patch: UpdateDict) -> str:
  keyed_or_nested_asgs: Dict = patch.get('injections', {})
  keyed = utils.dict2keyed(keyed_or_nested_asgs)
  config_man.commit_keyed_mfst_vars(keyed)
  return tam_client().apply([])


def run_hooks(from_ver: str, update: UpdateDict) -> List[ActionOutcome]:
  hooks = Hook.by_trigger(
    event=update['type'],
    from_ver=from_ver,
    to_ver=update['version']
  )

  outcomes = []
  for hook in hooks:
    outcomes.append(hook.action().run())

  return outcomes


def _gen_injection_telem(keys: List[str]):
  all_vars = config_man.read_mfst_vars()
  return {k: all_vars[k] for k in keys}
