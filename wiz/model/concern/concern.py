from wiz.model.step.step import Step
from wiz.model.base.wiz_model import WizModel


class Concern(WizModel):

  def __init__(self, config):
    super().__init__(config)
    self.description = config.get('description')

  def first_step_key(self) -> str:
    return self.config['steps'][0]

  def steps(self):
    return self.load_children('steps', Step)

  def step(self, key):
    return self.load_child('steps', Step, key)

