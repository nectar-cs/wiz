from nectwiz.model.operation.operation import Operation
from nectwiz.model.stage import serial as stage_serial


def ser_standard(operation: Operation):
  """
  Standard serializer for an Operation.
  :param operation: Operation instance.
  :return: serialized Operation dict.
  """
  return dict(
    id=operation.id(),
    title=operation.title,
    info=operation.info,
    synopsis=operation.synopsis
  )


def ser_full(operation: Operation):
  """
  Full serializer for an Operation - includes the Operation itself as well as
  related Stages and Prerequisites.
  :param operation: Operation instance.
  :return: serialized Operation dict.
  """
  stage_dicts = list(map(stage_serial.standard, operation.stages()))

  return dict(
    **ser_standard(operation),
    stages=stage_dicts
  )
