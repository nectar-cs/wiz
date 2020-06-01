from wiz.model.operations.operation import Operation
from wiz.model.prerequisite import serial as prereq_serial
from wiz.model.stage import serial as stage_serial


def standard(operation: Operation):
  return dict(
    id=operation.key,
    title=operation.title,
    description=operation.info,
    synopsis=operation.synopsis,
    affects_data=operation.affects_data,
    affects_uptime=operation.affects_uptime,
    res_access=operation.res_access()
  )


def full(operation: Operation):
  stage_dicts = [stage_serial.standard(s) for s in operation.stages()]
  prereq_dicts = [prereq_serial.standard(p) for p in operation.prerequisites()]

  return dict(
    **standard(operation),
    long_description=operation.long_desc,
    risks=operation.risks,
    stages=stage_dicts,
    prerequisites=prereq_dicts
  )
