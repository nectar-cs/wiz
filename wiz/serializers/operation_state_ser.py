from wiz.core.telem.ost import OperationState, StepState
from wiz.core.types import CommitOutcome, ExitConditionStatus, ExitConditionStatuses


def ser_commit_outcome(commit_outcome: CommitOutcome):
  return commit_outcome


def ser_exit_cond_outcome(outcome: ExitConditionStatus, polarity: str):
  return dict(
    **outcome,
    polarity=polarity
  )


def ser_exit_cond_outcomes(exit_outcomes: ExitConditionStatuses):
  positive_exit_outcomes = exit_outcomes.get('positive')
  negative_exit_outcomes = exit_outcomes.get('negative')
  return [
    [ser_exit_cond_outcome(o, 'positive') for o in positive_exit_outcomes],
    [ser_exit_cond_outcome(o, 'negative') for o in negative_exit_outcomes],
  ]


def ser_step_outcome(step_outcome: StepState):
  exit_outcomes = step_outcome.running_status.get('condition_statuses', {})

  return dict(
    stage_key=step_outcome.stage_id,
    step_key=step_outcome.step_id,
    started_at=str(step_outcome.started_at),
    committed_at=str(step_outcome.committed_at),
    terminated_at=str(step_outcome.terminated_at),
    commit_outcome=ser_commit_outcome(step_outcome.commit_outcome),
    exit_condition_outcomes=ser_exit_cond_outcomes(exit_outcomes)
  )


def serialize(op_state: OperationState):
  return dict(
    step_outcomes=list(map(ser_step_outcome, op_state.step_states or []))
  )
