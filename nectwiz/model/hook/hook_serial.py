from nectwiz.model.hook.hook import Hook


def standard(hook: Hook):
  return dict(
    id=hook.id(),
    title=hook._title,
    info=hook.info,
  )
