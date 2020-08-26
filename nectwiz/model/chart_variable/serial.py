from nectwiz.model.chart_variable.chart_variable import ChartVariable
from nectwiz.model.field import serial as field_serial
from nectwiz.model.operations.operation import Operation


def _mini_operation_ser(operation: Operation) -> dict:
  """
  Miniature serializer for the Operation instance.
  :param operation: Operation class instance.
  :return: serialized Operation object (dict).
  """
  return dict(
    id=operation.key,
    title=operation.title
  )


def standard(cv: ChartVariable, cache=None):
  """
  Standard serializer for the ChartVariable instance.
  :param cv: ChartVariable class instance.
  :param cache: cache to extract the chart value.
  :return: serialized ChartVariable object (dict).
  """
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
  """
  Extended serializer for the ChartVariable instance, which also includes includes
  details about the associated field.
  :param cv: ChartVariable class instance.
  :return: extended serialized ChartVariable object (dict).
  """
  field = cv.field()
  return dict(
    **standard(cv),
    field=(field and field_serial.without_meta(field))
  )
