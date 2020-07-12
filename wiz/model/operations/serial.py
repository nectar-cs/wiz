from wiz.core.telem.ost import OperationState
from wiz.model.operations.operation import Operation
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


def state(operation_state: OperationState):
  return dict(
    id=operation_state.osr_id,
    operation=operation_state.operation_id
  )


def full(operation: Operation):
  stage_dicts = [stage_serial.standard(s) for s in operation.stages()]
  # prereq_dicts = [prereq_serial.standard(p) for p in operation.prerequisites()]
  prereq_dicts = []

  return dict(
    **standard(operation),
    long_description=operation.long_desc,
    risks=operation.risks,
    stages=stage_dicts,
    prerequisites=prereq_dicts
  )
