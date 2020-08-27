from typing import Dict, List, Optional

from nectwiz.core import hub_client, config_man
from nectwiz.core.tam import tami_client
from nectwiz.core.tam.tam_provider import tam_client
from nectwiz.core.types import Update, UpdateOutcome
from nectwiz.core.wiz_app import wiz_app


def fetch_next_update() -> Optional[Update]:
  pass


def perform_update(update: Update) -> UpdateOutcome:
  release_outcome = {}
  if update.get('type') == 'release':
    release_outcome = apply_release(update)
  patch_outcome = apply_patch(update)
  telem = dict(**release_outcome, **patch_outcome)
  hub_client.post_update_outcome(telem)
  return telem


def apply_release(release: Update) -> UpdateOutcome:
  new_name = release.get('tami_name')
  tami_client.update_tami_name(new_name)
  wiz_app.reload_tami_name()
  out = tam_client().apply([])
  logs = out.split("\n") if out else []
  return UpdateOutcome(release_logs=logs)


def apply_patch(patch: Update) -> UpdateOutcome:
  assignments: Dict = patch.get('injections', {})
  pre_telem = _gen_injection_telem(list(assignments.keys()))
  config_man.commit_tam_vars(assignments)
  post_telem = _gen_injection_telem(list(assignments.keys()))
  out = tam_client().apply([])
  logs = out.split("\n") if out else []

  return UpdateOutcome(
    update_key=patch.get('id'),
    pre_inject=pre_telem,
    post_inject=post_telem,
    apply_logs=logs
  )


def _gen_injection_telem(keys: List[str]):
  all_vars = config_man.read_tam_vars()
  return {k: all_vars[k] for k in keys}
