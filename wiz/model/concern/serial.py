from wiz.model.concern.concern import Concern

def standard(concern: Concern):
  return dict(
    id=concern.key,
    title=concern.title,
    description=concern.description,
    first_step_id=concern.first_step_key()
  )
