from nectwiz.model.field.field import Field
from nectwiz.model.input import input_serializer


def embedded(field: Field):
  """
  Standard serializer for Field instances.
  :param field: Field instance.
  :return: serialized Field dict.
  """
  return dict(
    id=field.id(),
    title=field.title,
    info=field.info,
    is_inline=field.target == 'inline',
    needs_decorating=field.requires_decoration(),
    default=field.current_or_default(),
    **input_serializer.in_variable(field.input_spec()),
  )


def without_meta(field: Field):
  """
  Shortened serializer for Field instances, excludes meta info.
  :param field: Field instance.
  :return: serialized Field dict.
  """
  return dict(
    type=field.input_type,
    options=field.options(),
    default=field.default_value()
  )
