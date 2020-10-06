from typing import Dict

from nectwiz.core.core.config_man import config_man
from nectwiz.model.field.field import Field
from nectwiz.model.input import input_serializer
from nectwiz.model.operation.operation_state import OperationState
from nectwiz.model.operation.step import Step


def ser_embedded_field(field: Field, value, state: OperationState) -> Dict:
  decorated_value = None
  if field.delegate_variable():
    decorator = field.delegate_variable().value_decorator()
    if decorator:
      value = field.current_or_default() if value is None else value
      decorated_value = decorator.decorate(value, state)
  return dict(
    id=field.id(),
    title=field.title,
    info=field.info,
    is_inline=field.is_inline_chart_var(),
    default=field.current_or_default(),
    decorated_value=decorated_value,
    **input_serializer.in_variable(field.input_spec()),
  )


def ser_refreshed(step: Step, values: Dict, state: OperationState) -> Dict:
  """
  Standard serializer for a step.
  :param step: Step class instance.
  :param values: current user input
  :param state: current operation state
  :return: serialized Step in dict form.
  """
  config_man.read_manifest_vars()
  visible_fields = step.visible_fields(values, state)
  serialize_field = lambda field: ser_embedded_field(
    field=field,
    value=(values or {}).get(field.id()),
    state=state
  )
  return dict(
    id=step.id(),
    title=step.title,
    info=step.info,
    flags=[],
    fields=list(map(serialize_field, visible_fields))
  )
