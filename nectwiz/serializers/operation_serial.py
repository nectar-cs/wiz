from nectwiz.model.operation.operation import Operation
from nectwiz.model.operation.stage import Stage


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


def ser_embedded_stage(stage: Stage):
  """
  Standard serializer for a Stage.
  :param stage: Stage instance.
  :return: serialized Stage dict.
  """
  return dict(
    id=stage.id(),
    title=stage.title,
    description=stage.info,
    first_step_id=stage.first_step_id()
  )


def ser_full(operation: Operation):
  """
  Full serializer for an Operation - includes the Operation itself as well as
  related Stages and Prerequisites.
  :param operation: Operation instance.
  :return: serialized Operation dict.
  """
  stage_dicts = list(map(ser_embedded_stage, operation.stages()))

  return dict(
    **ser_standard(operation),
    stages=stage_dicts
  )
