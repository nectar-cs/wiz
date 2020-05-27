from wiz.model.operations.operation import Operation
from wiz.model.stage import serial as stage_serial


def standard(operation: Operation):
  return dict(
    id=operation.key,
    title=operation.title,
    description=operation.info,
    res_access=operation.res_access()
  )


def with_stages(operation: Operation):
  stage_ser = [stage_serial.standard(s) for s in operation.stages()]
  return dict(
    **standard(operation),
    stages=stage_ser
  )
