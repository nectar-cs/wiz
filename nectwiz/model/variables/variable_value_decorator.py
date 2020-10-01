from typing import Any, Dict

from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.operation.operation_state import OperationState


class VariableValueDecorator(WizModel):

  def __init__(self, config: Dict):
    super().__init__(config)
    self.output_template: str = config.get('template', '')

  def decorate(self, value: Any, operation_state: OperationState):
    subs = self.compute(value, operation_state) or {}
    return self.output_template.format(**subs)

  def compute(self, value: Any, operation_state: OperationState) -> Dict:
    return {}
