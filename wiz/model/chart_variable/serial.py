from wiz.model.chart_variable.chart_variable import ChartVariable
from wiz.model.field import serial as field_serial
from wiz.model.operations.operation import Operation


def _mini_operation_ser(operation: Operation):
  return dict(
    id=operation.key,
    title=operation.title
  )


def standard(cv: ChartVariable):
  ops_ser = [_mini_operation_ser(o) for o in cv.operations()]
  return dict(
    id=cv.key,
    title=cv.title,
    description=cv.info,
    is_safe_to_set=cv.is_safe_to_set(),
    operations=ops_ser
  )


def with_field(cv: ChartVariable):
  field = cv.field()
  return dict(
    **standard(cv),
    field=(field and field_serial.embedded(field))
  )
