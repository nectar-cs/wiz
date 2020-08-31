from nectwiz.model.chart_variable.chart_variable import ChartVariable
from nectwiz.model.field import serial as field_serial


def standard(cv: ChartVariable):
  """
  Standard serializer for the ChartVariable instance.
  :param cv: ChartVariable class instance.
  :param cache: cache to extract the chart value.
  :return: serialized ChartVariable object (dict).
  """
  return dict(
    id=cv.key,
    mode=cv.mode,
    description=cv.info,
    data_type=cv.data_type,
    default_value=cv.default_value,
    resource=cv.linked_res_name,
    category=cv.category,
    value=cv.read_crt_value(force_reload=False),
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
