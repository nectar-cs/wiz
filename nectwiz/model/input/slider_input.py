from typing import Dict

from nectwiz.model.input.input import GenericInput


class SliderInput(GenericInput):
  def __init__(self, config):
    super().__init__(config)
    self.min: int = config.get('min')
    self.max: int = config.get('max')
    self.step: int = config.get('step', 1)

  def extras(self) -> Dict[str, any]:
    return dict(
      min=self.min,
      max=self.max,
      step=self.step
    )

  def requires_decoration(self) -> bool:
    return True
