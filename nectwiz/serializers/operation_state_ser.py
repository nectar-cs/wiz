from nectwiz.core.telem.ost import OperationState, StepState
from nectwiz.core.core.types import CommitOutcome, ExitStatus, ExitStatuses


def ser_commit_outcome(commit_outcome: CommitOutcome):
  return commit_outcome


def ser_exit_cond_outcome(outcome: ExitStatus, polarity: str):
  return dict(
    key=outcome.get('key'),
    condition_met=outcome.get('met'),
    reason=outcome.get('reason'),
    resources_considered=outcome.get('resources_considered'),
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
  exit_outcomes = step_outcome.running_status.get('condition_statuses', {})

  return dict(
    stage_key=step_outcome.stage_id,
    step_key=step_outcome.step_id,
    started_at=str(step_outcome.started_at),
    committed_at=str(step_outcome.committed_at),
    terminated_at=str(step_outcome.terminated_at),
    commit_outcome_attributes=ser_commit_outcome(step_outcome.commit_outcome),
    exit_condition_outcomes_attributes=ser_exit_cond_outcomes(exit_outcomes)
  )


def serialize(op_state: OperationState):
  return dict(
    operation_key=op_state.op_id,
    step_outcomes_attributes=list(
      map(ser_step_outcome, op_state.step_states)
    )
  )
