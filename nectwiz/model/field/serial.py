from typing import Dict

from nectwiz.model.field.field import Field


def embedded(field: Field):
  """
  Standard serializer for Field instances.
  :param field: Field instance.
  :return: serialized Field dict.
  """
  return dict(
    id=field.key,
    title=field.title,
    type=field.type,
    options=field.options(),
    info=field.info,
    is_inline=field.target == 'inline',
    needs_decorating=field.needs_decorating(),
    default=field.default_value()
  )

def without_meta(field: Field):
  """
  Shortened serializer for Field instances, excludes meta info.
  :param field: Field instance.
  :return: serialized Field dict.
  """
  return dict(
    type=field.type,
    options=field.options(),
    default=field.default_value()
  )
