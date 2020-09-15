from typing import Dict, List, Optional

from nectwiz.core.core import utils, hub_client
from nectwiz.core.core.utils import dict2keyed

from nectwiz.core.core.config_man import config_man
from nectwiz.core.tam.tam_provider import tam_client
from nectwiz.core.core.types import UpdateDict, UpdateOutcome, ActionOutcome
from datetime import datetime

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
    tam_version=config_man.tam().get('ver'),
  )))
  print(f"[nw::updates_man] notif checked: {resp}")
  return resp.status_code < 205


def perform_update(update: UpdateDict) -> UpdateOutcome:
  pre_op_tam = config_man.mfst_vars(True)

  _type = update.get('type')
  if _type == TYPE_RELEASE:
    log_chunk = apply_upgrade(update)
  elif _type == TYPE_UPDATE:
    log_chunk = apply_update(update)
  else:
    raise RuntimeError(f"[nectwiz::updates_man] illegal update type '{_type}'")

  hook_outcomes = []
  if log_chunk is not None:
    from_ver = pre_op_tam.get('ver')
    hook_outcomes = run_hooks(from_ver, update)

  post_op_tam = config_man.mfst_vars(True)
  log_lines = log_chunk.split("\n") if log_chunk else []

  return UpdateOutcome(
    update_id=update.get('id'),
    type=_type,
    version=update.get('version'),
    apply_logs=log_lines,
    pre_man_vars=pre_op_tam,
    post_man_vars=post_op_tam,
    hook_outcomes=hook_outcomes
  )


def apply_upgrade(release: UpdateDict) -> str:
  config_man.patch_tam(dict(ver=release['version']))
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
