from typing import Any, Dict

from werkzeug.utils import cached_property

from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.operation.operation_state import OperationState


class VariableValueDecorator(WizModel):

  KEY_TEMPLATE = 'template'

  @cached_property
  def output_template(self) -> str:
    return self.get_prop(self.KEY_TEMPLATE, '')

  def decorate(self, value: Any, operation_state: OperationState):
    subs = self.compute(value, operation_state) or {}
    return self.output_template.format(**subs)

  def compute(self, value: Any, operation_state: OperationState) -> Dict:
    return {}
