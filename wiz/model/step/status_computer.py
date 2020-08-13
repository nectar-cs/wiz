from typing import List, Optional, Dict, Callable

from wiz.core import step_job_client
from wiz.core.telem.ost import StepState
from wiz.core.types import ExitConditionStatus, StepRunningStatus, ExitConditionStatuses, JobStatus
from wiz.model.predicate.predicate import Predicate
from wiz.model.step.step import Step

POS = 'positive'
NEG = 'negative'
TEC = Predicate
TECS = ExitConditionStatus
TSRS = StepRunningStatus


class StepStatusComputer:
  """Computes the status of all exit conditions for a given step."""

  def __init__(self, step: Step, own_state: StepState):
    self.step: Step = step
    self.own_state: Optional[StepState] = own_state

  # noinspection PyTypedDict
  def find_saved_cond_status(self, polarity: str, cond_id: str) -> Optional[TECS]:
    """
    Tries to locate and return the saved status of a given condition
    (specified by condition id), else returns None.
    :param polarity: "positive" or "negative" charge.
    :param cond_id: condition id to locate the appropriate condition.
    :return: status of a given condition or None.
    """
    if self.own_state:
      root: StepRunningStatus = self.own_state.running_status or {}
      polarities: ExitConditionStatuses = root.get('condition_statuses', {})
      statuses: List[ExitConditionStatus] = polarities.get(polarity, [])
      matcher = lambda ecs: ecs.get('key') == cond_id
      return next(filter(matcher, statuses), None)
    return None

  def eval_cond(self, condition: TEC) -> TECS:
    """
    Evaluates the passed condition and prepares an output with details of the
    evaluation.
    :param condition: condition to be evaluated.
    :return: dict with results of evaluation.
    """
    eval_result = condition.evaluate(self.own_state)
    return ExitConditionStatus(
      key=condition.key,
      met=eval_result,
      name=condition.title,
      resources_considered=condition.resources_considered
    )

  def eval_conds(self, charge: str, conditions: List[TEC]) -> List[TECS]:
    """
    Evaluates the list of passed conditions. Depending on halter selected, the
    evaluation may terminate early.
    :param charge: positive or negative. Early evaluation only possible with
    negative halters, and only when the condition evaluates to True. Reasoning:
    if any one negative condition evaluates to True, there is no point checking
    the rest. We know we failed.
    :param conditions: list of conditions to be evaluated.
    :return: list of condition statuses.
    """
    cond_statuses = []
    for condition in conditions:
      saved_cond_status = self.find_saved_cond_status(charge, condition.key)
      cond_status = saved_cond_status or self.eval_cond(condition)
      cond_statuses.append(cond_status)
      # if positive halters, this never evaluates to True, so we keep going
      # if negative halters, it cond_status is True, halter also returns True and the if clause triggers
      if halters[charge](cond_status['met']):
        return cond_statuses
    return cond_statuses

  def compute_status(self) -> StepRunningStatus:
    """
    Computes exit conditions statuses and merges with job completion status, if one
    exists.
    :return: instance of StepRunningStatus dict, with details of exit conditions
    evaluated and status assigned.
    """
    return StepRunningStatus(
      **self.compute_conditions_status(),
      job_status=self.compute_job_status()
    )

  def compute_job_status(self) -> Optional[JobStatus]:
    """
    Computes the condition status for a job.
    :return: job status or empty dict if no job defined.
    """
    if self.own_state and self.own_state.job_id:
      return step_job_client.compute_job_status(self.own_state.job_id)
    return {}

  def compute_conditions_status(self) -> StepRunningStatus:
    """
    Computes positive and negative conditions statuses for a given Step.
    Terminates when either ALL positive conditions have been met, or ANY one negative is met.
    Otherwise returns pending status.
    :return: instance of StepRunningStatus dict, with details of exit conditions
    evaluated and status assigned.
    """
    pos_conds = self.load_exit_conds(POS)
    neg_conds = self.load_exit_conds(NEG)

    pos_cond_statuses = self.eval_conds(POS, pos_conds)
    if all_conditions_met(pos_cond_statuses):
      return gen_step_exit_status(POS, pos_cond_statuses, [])

    neg_cond_statuses = self.eval_conds(NEG, neg_conds)
    if any_condition_met(neg_cond_statuses):
      return gen_step_exit_status(NEG, pos_cond_statuses, neg_cond_statuses)

    return gen_step_exit_status('pending', pos_cond_statuses, neg_cond_statuses)

  def load_exit_conds(self, charge:str) -> List[TEC]:
    """
    Loads exit conditions that will be checked. If explicit conditions are not
    defined by the vendor, Nectar's default conditions are used.
    :param charge: "positive" or "negative", specifies the type of default
    conditions to load.
    :return: list of Predicate class instances.
    """
    explicit = self.step.config.get('exit', {}).get(charge)
    if explicit is not None:
      return self.step.load_related(explicit, Predicate)
    else:
      return self.default_exit_conditions(charge)

  def default_exit_conditions(self, charge) -> List[TEC]:
    """
    Inflates (instantiates) a list of default conditions, positive or negative.
    One of 4 things can happen:
      1. If applies_manifest is positive, select resource default conditions are loaded
      2. If applies_manifest is negative, all/any resources default conditions are loaded
      3. If runs_job is positive, job-specific default conditions are loaded
      4. If none apply, an empty list is returned
    :param charge: "positive" or "negative", defines the kind of conditions to
    load.
    :return: list of Predicate class instances, or empty list.
    """
    if self.step.applies_manifest():
      if self.step.res_selector_descs:
        custom_cond_name = default_some_res_exit_conds[charge]
        custom_cond = Predicate.inflate(custom_cond_name)
        custom_cond.config['selector'] = self.step.res_selector_descs
        return [custom_cond]
      else:
        default_cond_names = default_res_exit_cond_ids[charge]
        return list(map(Predicate.inflate, default_cond_names))
    elif self.step.runs_job():
      default_cond_names = default_job_exit_conds[charge]
      return list(map(Predicate.inflate, default_cond_names))
    else:
      return []


def all_conditions_met(conditions: List[TECS]) -> bool:
  """
  Checks that all conditions in the passed list are met.
  :param conditions: list of conditions statuses, as TECS instances.
  :return: True if all conditions are True, else False.
  """
  return set([s['met'] for s in conditions]) == {True}


def any_condition_met(conditions: List[TECS]) -> bool:
  """
  Checks that at least one condition in the passed list is met.
  :param conditions: list of conditions statuses, as TECS instances.
  :return: True if at lease one condition is True, else False.
  """
  return True in [s['met'] for s in conditions]


def gen_step_exit_status(status, pos: List[TECS], neg: List[TECS]) -> TSRS:
  """
  Generates step exit status with details of all exit condition evaluations.
  :param status: desired status, eg "pending", "positive" or "negative".
  :param pos: list of positive conditions that was checked.
  :param neg: list of negative conditions that was checked.
  :return: instance of StepRunningStatus.
  """
  return StepRunningStatus(
    status=status,
    condition_statuses=ExitConditionStatuses(
      positive=pos,
      negative=neg
    )
  )


halters: Dict[str, Callable[[bool], bool]] = dict(
  positive=lambda status: False,
  negative=lambda status: status is True
)


default_some_res_exit_conds: Dict[str, str] = {
  POS: 'nectar.exit_conditions.select_resources_positive',
  NEG: 'nectar.exit_conditions.select_resources_negative',
}


default_res_exit_cond_ids: Dict[str, List[str]] = {
  POS: ['nectar.exit_conditions.all_resources_positive'],
  NEG: ['nectar.exit_conditions.any_resource_negative']
}


default_job_exit_conds: Dict[str, List[str]] = {
  POS: ['nectar.exit_conditions.job_in_succeeded_phase'],
  NEG: ['nectar.exit_conditions.job_in_failed_phase']
}
