import traceback
from typing import Dict, Any

from nectwiz.model.input.input import GenericInput


class SliderInput(GenericInput):
  def __init__(self, config):
    super().__init__(config)
    self.min: int = config.get('min')
    self.max: int = config.get('max')
    self.step: int = config.get('step', 1)
    self.suffix: str = config.get('suffix', '')

  def extras(self) -> Dict[str, any]:
    return dict(
      min=self.min,
      max=self.max,
      step=self.step,
      suffix=self.suffix
    )

  def sanitize_for_validation(self, value: Any) -> Any:
    if value is not None and self.suffix:
      # noinspection PyBroadException
      try:
        return float(str(value).split(self.suffix)[0])
      except:
        print("[nectwiz::slider_input] sanitize input failed:")
        print(traceback.format_exc())
        return value
    else:
      return value
