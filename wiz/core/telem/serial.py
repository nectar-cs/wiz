from typing import Dict, List

from typing_extensions import TypedDict

from wiz.core.telem.ost import OperationState, StepState
from wiz.core.types import ExitConditionStatus


class ApiExitConditionOutcome(TypedDict, total=True):
  condition_id: str
  condition_met: bool
  reason: str


class ApiStepOutcome(TypedDict, total=True):
  stage_id: str
  step_id: str
  started_at: str
  terminated_at: str
  commit_outcome: str
  chart_assigns: Dict
  state_assigns: Dict
  job_logs: List[str]
  exit_condition_outcomes: List[ApiExitConditionOutcome]
  outcome: str


class ApiOperationOutcome(TypedDict, total=True):
  operation_id: str
  step_outcomes: List[ApiStepOutcome]


def ser_exit_cond(cond_status: ExitConditionStatus) -> ApiExitConditionOutcome:
  return ApiExitConditionOutcome(
    condition_id=(cond_status.get('key') or cond_status.get('name')),
    condition_met=cond_status.get('met'),
    reason=cond_status.get('reason')
  )


def ser_step_state(step_state: StepState) -> ApiStepOutcome:
  commit_outcome = step_state.commit_outcome or {}
  final_status = step_state.running_status or {}
  outcome_word = final_status.get('status')

  final_conds = final_status.get('condition_statuses', {})
  relevant_conds = final_conds.get(outcome_word or 'negative')

  return ApiStepOutcome(
    stage_id=step_state.stage_id,
    step_id=step_state.step_id,
    started_at=nullify_empty(str(step_state.started_at)),
    terminated_at=nullify_empty(str(step_state.terminated_at)),
    commit_outcome=commit_outcome.get('status'),
    chart_assigns=commit_outcome.get('chart_assigns'),
    state_assigns=commit_outcome.get('state_assigns'),
    job_logs=step_state.job_logs,
    exit_condition_outcomes=list(map(ser_exit_cond, relevant_conds)),
    outcome=outcome_word
  )


def ser_op_state(op_state: OperationState) -> ApiOperationOutcome:
  return ApiOperationOutcome(
    operation_id=op_state.operation_id,
    step_outcomes=list(map(ser_step_state, op_state.step_states))
  )


nullify_empty = lambda s: s or None
