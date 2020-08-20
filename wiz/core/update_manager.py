from typing import Dict, List, Optional

from wiz.core import tami_client, hub_client
from wiz.core.types import Update, UpdateOutcome
from wiz.core.wiz_app import wiz_app


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
  out = tami_client.kubectl_apply()
  logs = out.split("\n") if out else []
  return UpdateOutcome(release_logs=logs)


def apply_patch(patch: Update) -> UpdateOutcome:
  assignments: Dict = patch.get('injections', {})
  pre_telem = _gen_injection_telem(list(assignments.keys()))
  tami_client.commit_values(assignments.items())
  post_telem = _gen_injection_telem(list(assignments.keys()))
  out = tami_client.kubectl_apply()
  logs = out.split("\n") if out else []

  return UpdateOutcome(
    update_key=patch.get('id'),
    pre_inject=pre_telem,
    post_inject=post_telem,
    apply_logs=logs
  )


def _gen_injection_telem(keys: List[str]):
  all_vars = tami_client.chart_dump()
  return {k: all_vars[k] for k in keys}
