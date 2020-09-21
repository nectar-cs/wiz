from typing import Dict

from nectwiz.model.input.input import Input


class SliderInput(Input):
  def __init__(self, config):
    super().__init__(config)
    self.min: int = config.get('min')
    self.max: int = config.get('max')
    self.step: int = config.get('step')

  def extras(self) -> Dict[str, any]:
    return dict(
      min=self.min,
      max=self.max,
      step=self.step
    )
