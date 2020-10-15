from datetime import datetime

from nectwiz.model.operation.operation_state import OperationState


def record(op_state: OperationState):
  return dict(
    status=op_state.status,
    occurred_at=datetime.now(),
    tasks=[
      op_state.preflight_telem,
      *[s.action_telem for s in op_state.step_states]
    ]
  )
