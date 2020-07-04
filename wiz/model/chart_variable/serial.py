from wiz.model.chart_variable.chart_variable import ChartVariable
from wiz.model.field import serial as field_serial
from wiz.model.operations.operation import Operation


def _mini_operation_ser(operation: Operation):
  return dict(
    id=operation.key,
    title=operation.title
  )


def standard(cv: ChartVariable, cache=None):
  ops_ser = [_mini_operation_ser(o) for o in cv.operations()]
  return dict(
    id=cv.key,
    mode=cv.mode,
    description=cv.info,
    data_type=cv.data_type,
    default_value=cv.default_value,
    resource=cv.linked_res_name,
    category=cv.category,
    value=cv.read_crt_value(cache),
    operations=ops_ser
  )


def with_field(cv: ChartVariable):
  field = cv.field()
  return dict(
    **standard(cv),
    field=(field and field_serial.without_meta(field))
  )
