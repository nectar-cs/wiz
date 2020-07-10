from functools import cached_property
from typing import Dict, Optional

from wiz.core import tedi_client, utils


cmap_field = 'sharing_prefs'
upload_telem_key = 'upload_telem'

class SharingPerms:

  @cached_property
  def user_perms(self) -> Dict:
    kat_map = tedi_client.master_cmap()
    return kat_map.jget(cmap_field, {}) if kat_map else {}

  def can_sync_telem(self) -> bool:
    return x_to_bool(self.user_perms.get(upload_telem_key))

  def can_share_prop(self, prop: str) -> bool:
    if not utils.is_dev():
      category = find_prop_category(prop)
      return x_to_bool(category and self.user_perms.get(category))
    else:
      return True


def x_to_bool(raw) -> bool:
  if raw is None:
    return False
  if type(raw) == bool:
    return raw
  elif type(raw) == bool:
    return raw.lower() == 'true'


def find_prop_category(prop) -> Optional[str]:
  for category, category_props in category_props_mapping.items():
    if prop in category_props:
      return category
  return None


category_props_mapping = {
  'operations.metadata': [
    'operation_outcome.operation_id',
    'operation_outcome.step_outcomes',
    'operation_outcome.step_outcomes.stage_id',
    'operation_outcome.step_outcomes.step_id',
    'operation_outcome.step_outcomes.started_at',
    'operation_outcome.step_outcomes.terminated_at',
    'operation_outcome.step_outcomes.job_logs',
    'operation_outcome.step_outcomes.commit_outcome',
    'operation_outcome.step_outcomes.exit_condition_outcomes',
    'operation_outcome.step_outcomes.exit_condition_outcomes.condition_id',
    'operation_outcome.step_outcomes.exit_condition_outcomes.condition_met',
    'operation_outcome.step_outcomes.exit_condition_outcomes.reason'
  ],
  'operations.assignments': [
    'operation_outcome.step_outcomes.chart_assigns',
    'operation_outcome.step_outcomes.state_assigns',
  ],
}
