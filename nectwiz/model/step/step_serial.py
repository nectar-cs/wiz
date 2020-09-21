from typing import Dict

from nectwiz.core.core.config_man import config_man
from nectwiz.model.field import serial as field_serial
from nectwiz.model.operation.operation_state import OperationState
from nectwiz.model.step.step import Step


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
  vis_fields = step.visible_fields(values, op_state)

  return dict(
    id=step.id(),
    title=step.title,
    info=step.info,
    flags=[],
    fields=[ser_field(f) for f in vis_fields]
  )
