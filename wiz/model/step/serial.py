from wiz.model.step.step import Step


def standard(step: Step):
  return dict(
    id=step.key,
    title=step.title,
  )
