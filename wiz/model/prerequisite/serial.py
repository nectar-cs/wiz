from wiz.model.prerequisite.prerequisite import Prerequisite


def standard(prereq: Prerequisite):
  return dict(
    id=prereq.key,
    title=prereq.title
  )
