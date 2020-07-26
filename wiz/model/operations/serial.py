from wiz.core.telem.ost import OperationState
from wiz.model.operations.operation import Operation
from wiz.model.stage import serial as stage_serial


def ser_standard(operation: Operation):
  """
  Standard serializer for an Operation.
  :param operation: Operation instance.
  :return: serialized Operation dict.
  """
  return dict(
    id=operation.key,
    title=operation.title,
    description=operation.info,
    synopsis=operation.synopsis,
    affects_data=operation.affects_data,
    affects_uptime=operation.affects_uptime,
    res_access=operation.res_access()
  )


def ser_state(operation_state: OperationState):
  """
  Serializer for an Operation State.
  :param operation_state: Operation State instance.
  :return: serialized Operation State dict.
  """
  return dict(
    id=operation_state.osr_id,
    operation=operation_state.operation_id
  )

def ser_embedded_prereq(prereq):
  """
  Serializer for an Embedded Prerequisite.
  :param prereq: Prerequisite instance.
  :return: serialized Prerequisite dict.
  """
  return dict(
    id=prereq.key,
    title=prereq.title,
    description=prereq.info
  )


def ser_full(operation: Operation):
  """
  Full serializer for an Operation - includes the Operation itself as well as
  related Stages and Prerequisites.
  :param operation: Operation instance.
  :return: serialized Operation dict.
  """
  stage_dicts = list(map(stage_serial.standard, operation.stages()))
  prereq_dicts = list(map(ser_embedded_prereq, operation.prerequisites()))

  return dict(
    **ser_standard(operation),
    long_description=operation.long_desc,
    risks=operation.risks,
    stages=stage_dicts,
    pre_requisites=prereq_dicts
  )
