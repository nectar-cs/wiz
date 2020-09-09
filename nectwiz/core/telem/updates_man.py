from typing import Dict, List, Optional

from nectwiz.core.core import config_man
from nectwiz.core.tam.tam_provider import tam_client
from nectwiz.core.core.types import Update, UpdateOutcome
from nectwiz.core.core.wiz_app import wiz_app
from datetime import datetime


def fetch_next_update() -> Optional[Update]:
  config_man.write_last_update_checked(str(datetime.now()))
  return None


def perform_update(update: Update) -> UpdateOutcome:
  release_outcome = {}
  if update.get('type') == 'release':
    new_tam_version = update['tam_version']
    wiz_app.change_tam_version(new_tam_version)
  patch_outcome = apply_patch(update)
  telem = dict(**release_outcome, **patch_outcome)
  return telem


def apply_patch(patch: Update) -> UpdateOutcome:
  assignments: Dict = patch.get('injections', {})
  keyed = list(assignments.items())
  pre_telem = _gen_injection_telem(keyed)
  config_man.commit_keyed_tam_assigns(keyed)
  post_telem = _gen_injection_telem(keyed)
  out = tam_client().apply([])
  logs = out.split("\n") if out else []

  return UpdateOutcome(
    update_key=patch.get('id'),
    pre_inject=pre_telem,
    post_inject=post_telem,
    apply_logs=logs
  )


def _gen_injection_telem(keys: List[str]):
  all_vars = config_man.read_man_vars()
  return {k: all_vars[k] for k in keys}
