from wiz.model.stage.stage import Stage


def standard(stage: Stage):
  """
  Standard serializer for a Stage.
  :param stage: Stage instance.
  :return: serialized Stage dict.
  """
  return dict(
    id=stage.key,
    title=stage.title,
    description=stage.info,
    first_step_id=stage.first_step_key()
  )
