from typing import List, Optional

from nectwiz.core.core.types import PredEval
from nectwiz.model.predicate.predicate import Predicate
from nectwiz.model.step.step_state import StepState

POS = 'positive'
NEG = 'negative'
TPD = Predicate
TEXS = PredEval


def eval_pred(predicate: Predicate) -> PredEval:
  eval_result = predicate.evaluate()
  return PredEval(
    key=predicate.key,
    met=eval_result,
    name=predicate.title,
  )


def eval_preds(predicates: List[TPD], charge: str, prev_state: StepState):
  for predicate in predicates:
    prev_eval = find_prev_cs(prev_state, charge, predicate.id())
    if not prev_eval or needs_recomputing(prev_eval, charge):
      final_eval = eval_pred(predicate)
      prev_state.notify_exit_status_computed(charge, final_eval)
      if can_halt_early(final_eval, charge):
        return


def can_halt_early(pred_eval: PredEval, charge) -> bool:
  return pred_eval['met'] and charge == NEG


def needs_recomputing(pred_eval: PredEval, charge: str) -> bool:
  return charge == NEG or not pred_eval['met']


def compute(predicates_root, step_state: StepState):
  pos_preds = predicates_root.get(POS)
  neg_preds = predicates_root.get(NEG)

  eval_preds(pos_preds, POS, step_state)
  if all_conditions_met(step_state.exit_statuses[POS]):
    step_state.notify_succeeded()

  eval_preds(neg_preds, NEG, step_state)
  if any_condition_met(step_state.exit_statuses[POS]):
    step_state.notify_failed()


def all_conditions_met(conditions: List[TEXS]) -> bool:
  return set([s['met'] for s in conditions]) == {True}


def any_condition_met(conditions: List[TEXS]) -> bool:
  return True in [s['met'] for s in conditions]


def find_prev_cs(prev_state: StepState, polarity, cond_id) -> Optional[TEXS]:
  root = prev_state.exit_statuses or {}
  statuses: List[TEXS] = root.get(polarity, [])
  matcher = lambda ecs: ecs.get('key') == cond_id
  return next(filter(matcher, statuses), None)
