from nectwiz.model.input import input_serializer
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
    value=cv.read_crt_value(force_reload=False)    
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
