from wiz.model.stage.stage import Stage


def standard(stage: Stage):
  return dict(
    id=stage.key,
    title=stage.title,
    description=stage.info,
    first_step_id=stage.first_step_key()
  )
