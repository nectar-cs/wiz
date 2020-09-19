from nectwiz.core.core.types import PredEval, ExitStatuses
from nectwiz.model.operation.operation_state import OperationState
from nectwiz.model.step.step_state import StepState


def ser_exit_cond_outcome(outcome: PredEval, polarity: str):
  return dict(
    key=outcome.get('predicate_id'),
    condition_met=outcome.get('met'),
    reason=outcome.get('reason'),
    resources_considered=[],
    polarity=polarity
  )


def ser_exit_cond_outcomes(exit_outcomes: ExitStatuses):
  positive_exit_outcomes = exit_outcomes.get('positive', [])
  negative_exit_outcomes = exit_outcomes.get('negative', [])
  return (
    [ser_exit_cond_outcome(o, 'positive') for o in positive_exit_outcomes] +
    [ser_exit_cond_outcome(o, 'negative') for o in negative_exit_outcomes]
  )


def ser_step_outcome(step_outcome: StepState):
  exit_outcomes = step_outcome.exit_statuses

  stage_id, step_id = step_outcome.step_sig.split('::')

  return dict(
    stage_key=stage_id,
    step_key=step_id,
    started_at=str(step_outcome.started_at),
    committed_at=str(step_outcome.committed_at),
    terminated_at=str(step_outcome.terminated_at),
    commit_outcome_attributes=step_outcome.action_outcome,
    exit_condition_outcomes_attributes=ser_exit_cond_outcomes(exit_outcomes)
  )


def serialize(op_state: OperationState):
  return dict(
    operation_key=op_state.op_id,
    step_outcomes_attributes=list(
      map(ser_step_outcome, op_state.step_states)
    )
  )
