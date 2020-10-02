from typing import Any, Dict

from nectwiz.model.operation.operation_state import OperationState
from nectwiz.model.variables.variable_value_decorator import VariableValueDecorator


class FixedReplicasDecorator(VariableValueDecorator):
  def compute(self, value: Any, operation_state: OperationState) -> Dict:
    if type(value) == int or (value or '').isdigit():
      replicas = int(value)
      return dict(
        size="small" if replicas < 10 else "large",
        cost=replicas * 7,
        volume=replicas * 10
      )
