from typing import Dict, List, Optional

from nectwiz.core.core.utils import dict2keyed

from nectwiz.core.core.config_man import config_man
from nectwiz.core.tam.tam_provider import tam_client
from nectwiz.core.core.types import UpdateDict, UpdateOutcome
from datetime import datetime

from nectwiz.model.chart_variable.chart_variable import ChartVariable


def fetch_next_update() -> Optional[UpdateDict]:
  config_man.write_last_update_checked(str(datetime.now()))
  return None


def perform_update(update: UpdateDict) -> UpdateOutcome:
  pre_op_tam = config_man.mfst_vars(True)
  _type = update.get('type')
  if _type == 'release':
    log_chunk = apply_release_update(update)
  elif _type == 'patch':
    log_chunk = apply_patch_update(update)
  else:
    raise RuntimeError(f"[nectwiz::updates_man] bad update type {_type}")

  post_op_tam = config_man.mfst_vars(True)
  log_lines = log_chunk.split("\n") if log_chunk else []

  return UpdateOutcome(
    update_id=update.get('id'),
    apply_logs=log_lines,
    pre_man_vars=pre_op_tam,
    post_man_vars=post_op_tam
  )


def apply_release_update(release: UpdateDict) -> str:
  config_man.patch_tam(dict(ver=release['version']))
  target_var_ids = [cv.id() for cv in ChartVariable.release_dependent_vars()]
  new_man_defs = dict2keyed(tam_client().load_manifest_defaults())
  overridden_vars = [e for e in new_man_defs if e[0] in target_var_ids]
  config_man.commit_keyed_mfst_vars(overridden_vars)
  return tam_client().apply([])


def apply_patch_update(patch: UpdateDict) -> str:
  assignments: Dict = patch.get('injections', {})
  keyed = list(assignments.items())
  config_man.commit_keyed_mfst_vars(keyed)
  return tam_client().apply([])


def _gen_injection_telem(keys: List[str]):
  all_vars = config_man.read_mfst_vars()
  return {k: all_vars[k] for k in keys}
