from functools import cached_property
from typing import Dict, Optional

from wiz.core import tedi_client, utils


class SharingPerms:

  @cached_property
  def user_perms(self) -> Dict:
    kat_map = tedi_client.master_cmap()
    return kat_map.jget('sharing_prefs', {}) if kat_map else {}

  def can_sync_telem(self) -> bool:
    return self.user_perms.get('upload_telem')

  def can_share_prop(self, prop: str) -> bool:
    if not utils.is_dev():
      category = find_prop_category(prop)
      if category:
        return self.user_perms.get(category)
      else:
        print(f"DANGER unaffiliated sharing prop {prop}")
        return False
    else:
      return True


def find_prop_category(prop) -> Optional[str]:
  for category, category_props in category_props_mapping:
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
