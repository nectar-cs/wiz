from typing import List, Optional, Dict, Callable

from wiz.core.types import ExitConditionStatus, StepExitStatus, ExitConditionStatuses
from wiz.model.step.exit_condition import ExitCondition
from wiz.model.step.step import Step

POS = 'positive'
NEG = 'negative'
TEC = ExitCondition
TECS = ExitConditionStatus
TSES = StepExitStatus

class StepStatusComputer:

  def __init__(self, step: Step, op_state):
    self.step = step
    self.op_state = op_state
    self.own_state = step.find_own_state(op_state)

  def find_saved_cond_status(self, _type: str, cond_id: str) -> Optional[TECS]:
    if self.own_state:
      root = self.own_state.exit_condition_status.get(_type)
      return root.get(cond_id) if root else None
    return None

  def eval_cond(self, condition: TEC) -> TECS:
    eval_result = condition.evaluate(self.own_state)
    return ExitConditionStatus(
      key=condition.key,
      met=eval_result,
      name=condition.title,
      resources_considered=condition.resources_considered
    )

  def eval_conds(self, charge: str, conditions: List[TEC]) -> List[TECS]:
    cond_statuses = []
    for condition in conditions:
      saved_cond_status = self.find_saved_cond_status(charge, condition.key)
      cond_status = saved_cond_status or self.eval_cond(condition)
      cond_statuses.append(cond_status)
      if halters[charge](cond_status['met']):
        return cond_statuses
    return cond_statuses

  def compute_status(self) -> StepExitStatus:
    pos_conds = self.load_type_exit_conds(POS)
    neg_conds = self.load_type_exit_conds(NEG)
    pos_cond_statuses = self.eval_conds(POS, pos_conds)

    if all_conditions_met(pos_cond_statuses):
      return gen_step_exit_status(POS, pos_cond_statuses, [])

    neg_cond_statuses = self.eval_conds(NEG, neg_conds)
    if any_condition_met(neg_cond_statuses):
      return gen_step_exit_status(NEG, pos_cond_statuses, neg_cond_statuses)

    return gen_step_exit_status('pending', pos_cond_statuses, neg_cond_statuses)

  def load_type_exit_conds(self, charge) -> List[TEC]:
    explicit = self.step.config.get('exit', {}).get(charge)
    if explicit is not None:
      return self.step.load_related(explicit, ExitCondition)
    else:
      return self.default_exit_conditions(charge)

  def default_exit_conditions(self, charge) -> List[TEC]:
    if self.step.applies_manifest():
      if self.step.res_selector_descs:
        custom_cond_name = default_some_res_exit_conds[charge]
        custom_cond = ExitCondition.inflate(custom_cond_name)
        custom_cond.config['selector'] = self.step.res_selector_descs
        return [custom_cond]
      else:
        default_cond_names = default_res_exit_cond_ids[charge]
        return list(map(ExitCondition.inflate, default_cond_names))
    elif self.step.runs_job():
      default_cond_names = default_job_exit_conds[charge]
      return list(map(ExitCondition.inflate, default_cond_names))
    else:
      return []


def all_conditions_met(conditions: List[TECS]) -> bool:
  return set([s['met'] for s in conditions]) == {True}


def any_condition_met(conditions: List[TECS]) -> bool:
  return True in conditions


def gen_step_exit_status(status, pos: List[TECS], neg: List[TECS]) -> TSES:
  return StepExitStatus(
    status=status,
    condition_statuses=ExitConditionStatuses(
      positive=pos,
      negative=neg
    )
  )


halters: Dict[str, Callable[[bool], bool]] = dict(
  positive=lambda status: False,
  negative=lambda status: status == True
)


default_some_res_exit_conds: Dict[str, str] = {
  POS: 'nectar.exit_conditions.select_resources_positive',
  NEG: 'nectar.exit_conditions.select_resources_positive',
}


default_res_exit_cond_ids: Dict[str, List[str]] = {
  POS: ['nectar.exit_conditions.all_resources_positive'],
  NEG: ['nectar.exit_conditions.any_resource_negative']
}


default_job_exit_conds: Dict[str, List[str]] = {
  POS: ['nectar.exit_conditions.job_in_succeeded_phase'],
  NEG: ['nectar.exit_conditions.job_in_failed_phase']
}
