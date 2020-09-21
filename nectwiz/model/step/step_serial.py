from typing import Dict

from nectwiz.core.core.config_man import config_man
from nectwiz.model.field import serial as field_serial
from nectwiz.model.step.step import Step


def standard(step: Step) -> Dict:
  """
  Standard serializer for a step.
  :param step: Step class instance.
  :return: serialized Step in dict form.
  """
  config_man.read_mfst_vars()
  ser_field = lambda f: field_serial.embedded(f)

  return dict(
    id=step.id(),
    title=step.title,
    info=step.info,
    flags=[],
    fields=[ser_field(f) for f in step.fields()]
  )
