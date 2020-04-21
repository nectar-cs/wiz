from wiz.core import core


class ApplyCommit:

  def __init__(self, values):
    self.values = values

  def safe_values(self):
    core.commit_values()
