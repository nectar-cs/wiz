from nectwiz.model.field import serial as field_serial
from nectwiz.model.variables.manifest_variable import ManifestVariable


def standard(cv: ManifestVariable):
  """
  Standard serializer for the ChartVariable instance.
  :param cv: ChartVariable class instance.
  :return: serialized ChartVariable object (dict).
  """
  return dict(
    id=cv.id(),
    mode=cv.mode,
    description=cv.info,
    default_value=cv.default_value(),
    value=cv.read_crt_value(force_reload=False),
  )


def with_field(cv: ManifestVariable):
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
