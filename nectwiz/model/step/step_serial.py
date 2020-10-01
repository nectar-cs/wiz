from typing import Dict

from nectwiz.core.core.config_man import config_man
from nectwiz.model.field.field import Field
from nectwiz.model.input import input_serializer
from nectwiz.model.operation.operation_state import OperationState
from nectwiz.model.step.step import Step


def field_serial(field: Field):
  """
  Standard serializer for Field instances.
  :param field: Field instance.
  :return: serialized Field dict.
  """
  return dict(
    id=field.id(),
    title=field.title,
    info=field.info,
    is_inline=field.is_inline_chart_var(),
    default=field.current_or_default(),
    **input_serializer.in_variable(field.input_spec()),
  )


def standard(step: Step, values: Dict, op_state: OperationState) -> Dict:
  """
  Standard serializer for a step.
  :param step: Step class instance.
  :param values: current user input
  :param op_state: current operation state
  :return: serialized Step in dict form.
  """
  config_man.read_mfst_vars()
  ser_field = lambda f: field_serial.embedded(f)
  visible_fields = step.visible_fields(values, op_state)

  return dict(
    id=step.id(),
    title=step.title,
    info=step.info,
    flags=[],
    fields=list(map(ser_field, visible_fields))
  )

def for_refresh(step: Step, values: Dict, op_state: OperationState) -> Dict:
  config_man.read_mfst_vars()
  ser_field = lambda f: field_serial.embedded(f)
  visible_fields = step.visible_fields(values, op_state)
