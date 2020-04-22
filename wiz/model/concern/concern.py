from wiz.model.step.step import Step
from wiz.model.base.wiz_model import WizModel


class Concern(WizModel):

  def __init__(self, config):
    super().__init__(config)
    self.description = config.get('description')

  def first_step_key(self) -> str:
    return self.config['steps'][0]

  def step(self, key) -> Step:
    step_key = [s for s in self.config['steps'] if s == key][0]
    return Step.inflate(step_key)

