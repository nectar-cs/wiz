from typing import Optional

from wiz.core import step_job_client
from wiz.model.base import res_selector
from wiz.model.base.wiz_model import WizModel


class ExitCondition(WizModel):

  @property
  def cond_type(self):
    return self.config.get('type')

  def evaluate(self, step_state) -> Optional[bool]:
    if self.cond_type == 'resource_ternary_statuses':
      return self.eval_ternary_statuses()

    elif self.cond_type == 'job_pod_phase':
      return self.eval_for_job_exec(step_state)

    else:
      print("DANGER don't know condition type " + self.cond_type)
      return None

  def eval_for_job_exec(self, step_state) -> bool:
    check_against = self.config.get('check_against', 'Succeeded')
    kat_job = step_job_client.find_job(step_state.job_id)
    return kat_job.pods()[0].phase.status == check_against

  def eval_ternary_statuses(self) -> bool:
    selector_config = self.config.get('selector', '*:*')
    match_type = self.config.get('match', 'all')
    check_against = self.config.get('check_against', 'positive')

    res_list = res_selector.res_sel_to_res(selector_config)
    ternary_statuses = [r.ternary_status for r in res_list]

    if match_type == 'all':
      return set(ternary_statuses) == {check_against}

    elif match_type == 'one':
      return check_against in ternary_statuses

    else:
      print("DANGER DONT KNOW MATCH TYPE" + match_type)
      return False

