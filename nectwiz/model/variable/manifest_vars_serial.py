from nectwiz.model.input import input_serializer
from nectwiz.model.variable.manifest_variable import ManifestVariable


def standard(cv: ManifestVariable, reload=True):
  return dict(
    id=cv.id(),
    title=cv.title,
    mode=cv.mode,
    description=cv.info,
    default_value=cv.default_value(reload),
    value=cv.read_crt_value(reload),
    is_valid=cv.is_currently_valid()
  )


def full(cv: ManifestVariable):
  """
  Extended serializer for the ChartVariable instance, which also includes includes
  details about the associated field.
  :param cv: ChartVariable class instance.
  :return: extended serialized ChartVariable object (dict).
  """
  return dict(
    **standard(cv),
    **input_serializer.in_variable(cv.input_spec())
  )
