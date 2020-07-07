from functools import cached_property
from typing import Dict, Optional

from wiz.core.osr import OperationState, StepState
from wiz.core.sharing_perms import SharingPerms
from wiz.model.operations.operation import Operation


class OperationStateSerializer:

  @cached_property
  def sharing_perms(self) -> SharingPerms:
    return SharingPerms()

  def if_allowed(self, prop_name, value) -> Optional:
    can_share = self.sharing_perms.can_share_prop(prop_name)
    return value if can_share else None

  def sanitize_ser(self, unsafe: Dict):
    return {k: self.if_allowed(k, v) for k, v in unsafe.items()}

  def ser_step_state(self, step_state: StepState) -> Dict:
    return self.sanitize_ser(dict(
      commit_outcome=step_state.commit_outcome,
      commit_reason=step_state.commit_reason,
      committed_at=none_less_str(step_state.committed_at),

      chart_assignments=step_state.chart_assigns,
      state_assignments=step_state.state_assigns,

      terminated_at=none_less_str(step_state.terminated_at),
      outcome=step_state.outcome,
      job_logs=step_state.job_logs,
    ))

  def serialize(self, op_state: OperationState) -> Dict:
    operation: Operation = Operation.find_state_owner(op_state.operation_id)

    return self.sanitize_ser(dict(
      operation_id=op_state.operation_id,
      operation_name=operation.title,
      step_states=list(map(self.__class__.ser_step_state, op_state.step_states))
    ))

def none_less_str(value):
  return str(value) if value is not None else None
