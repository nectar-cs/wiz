from wiz.core.wiz_globals import wiz_globals
from wiz.model.step.step import Step
from wiz.model.wiz_model import WizModel


class Concern(WizModel):

  def __init__(self, config):
    super().__init__(config)
    self.key = config['key']
    self.title = config.get('title')
    self.description = config.get('description')

  def first_step_key(self) -> str:
    return self.config['steps'][0]

  def step(self, key) -> Step:
    step_key = [s for s in self.config['steps'] if s == key][0]
    step_config = wiz_globals.step_config(step_key)
    return Step.inflate(step_config)

