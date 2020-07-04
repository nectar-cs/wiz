from wiz.model.field import serial as field_serial
from wiz.model.step.step import Step


def standard(step: Step):
  return dict(
    id=step.key,
    title=step.title,
    info=step.info,
    flags=step.flags,
    fields=[field_serial.embedded(f) for f in step.fields()]
  )
