from typing import List, Optional, Dict, Callable

from nectwiz.core.core.types import ExitStatus, ExitStatuses
from nectwiz.model.predicate.predicate import Predicate
from nectwiz.model.step.step_state import StepState

POS = 'positive'
NEG = 'negative'
TPD = Predicate
TEXS = ExitStatus


def eval_cond(condition: Predicate) -> ExitStatus:
  """
  Evaluates the passed condition and prepares an output with details of the
  evaluation.
  :param condition: condition to be evaluated.
  :return: dict with results of evaluation.
  """
  eval_result = condition.evaluate()
  return ExitStatus(
    key=condition.key,
    met=eval_result,
    name=condition.title,
  )


def eval_conds(predicates: List[TPD], polarity: str, prev_state) -> List[TEXS]:
  cond_statuses = []
  for predicate in predicates:
    saved_cond_status = find_prev_cs(prev_state, polarity, predicate.id())
    saved_cond_status = discriminate_saved_cond(polarity, saved_cond_status)
    cond_status: TEXS = saved_cond_status or eval_cond(predicate)
    cond_statuses.append(cond_status)
    if halters[polarity](cond_status['met']):
      return cond_statuses
  return cond_statuses


def compute_status(exit_conds, prev_state: StepState) -> List[ExitStatus]:
  """
  Computes positive and negative conditions statuses for a given Step.
  Terminates when either ALL positive conditions have been met, or ANY one negative is met.
  Otherwise returns pending status.
  :return: instance of StepRunningStatus dict, with details of exit conditions
  evaluated and status assigned.
  """
  pos_conds = load_exit_conds(exit_conds, POS)
  neg_conds = load_exit_conds(exit_conds, POS)

  pos_cond_statuses = eval_conds(pos_conds, POS, prev_state)
  if all_conditions_met(pos_cond_statuses):
    return gen_step_exit_status(POS, pos_cond_statuses, [])

  return gen_step_exit_status('pending', pos_cond_statuses, neg_cond_statuses)

def load_exit_conds(exit_conds, charge: str) -> List[TPD]:
  """
  Loads exit conditions that will be checked. If explicit conditions are not
  defined by the vendor, Nectar's default conditions are used.
  :return: list of Predicate class instances.
  """
  explicit = exit_conds.get(charge)
  if explicit is not None:
    return self.step.load_related(explicit, Predicate)
  else:
    return self.default_exit_conditions(charge)

def default_exit_conditions(self, charge) -> List[TPD]:
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
  elif self.step.triggers_action():
    default_cond_names = default_job_exit_conds[charge]
    return list(map(Predicate.inflate, default_cond_names))
  else:
    return []


def all_conditions_met(conditions: List[TEXS]) -> bool:
  """
  Checks that all conditions in the passed list are met.
  :param conditions: list of conditions statuses, as TECS instances.
  :return: True if all conditions are True, else False.
  """
  return set([s['met'] for s in conditions]) == {True}


def any_condition_met(conditions: List[TEXS]) -> bool:
  """
  Checks that at least one condition in the passed list is met.
  :param conditions: list of conditions statuses, as TECS instances.
  :return: True if at lease one condition is True, else False.
  """
  return True in [s['met'] for s in conditions]


def find_prev_cs(prev_state: StepState, polarity, cond_id) -> Optional[TEXS]:
  root = prev_state.exit_statuses or {}
  statuses: List[TEXS] = root.get(polarity, [])
  matcher = lambda ecs: ecs.get('key') == cond_id
  return next(filter(matcher, statuses), None)


def gen_step_exit_status(status, pos: List[TEXS], neg: List[TEXS]) -> TSRS:
  """
  Generates step exit status with details of all exit condition evaluations.
  :param status: desired status, eg "pending", "positive" or "negative".
  :param pos: list of positive conditions that was checked.
  :param neg: list of negative conditions that was checked.
  :return: instance of StepRunningStatus.
  """
  return StepRunningStatus(
    status=status,
    condition_statuses=ExitStatuses(
      positive=pos,
      negative=neg
    )
  )


def discriminate_saved_cond(polarity: str, status: TEXS) -> Optional[TEXS]:
  """
  Determines whether a past condition status is relevant in
  computing the current status.
  :param polarity: positive or negative
  :param status: the saved status if one exists
  :return: true only for pos-needing conditions that were already pos
  """
  if status is not None and polarity == POS:
    return status if status.get('met') else None
  else:
    return None


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

