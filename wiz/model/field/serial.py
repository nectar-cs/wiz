from wiz.model.field.field import Field


def embedded(field: Field):
  return dict(
    id=field.key,
    title=field.title,
    type=field.type,
    options=field.options(),
    info=field.info,
    is_inline=field.is_inline,
    needs_decorating=field.needs_decorating(),
    default=field.default_value()
  )

def without_meta(field: Field):
  return dict(
    type=field.type,
    options=field.options(),
    default=field.default_value()
  )
