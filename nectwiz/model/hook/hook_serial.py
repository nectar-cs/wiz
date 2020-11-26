from nectwiz.model.hook.hook import Hook


def standard(hook: Hook):
  return dict(
    id=hook.id(),
    title=hook.title,
    info=hook.info,
  )
