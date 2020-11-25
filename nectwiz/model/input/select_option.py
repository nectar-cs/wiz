from typing import Dict

from nectwiz.model.base.wiz_model import WizModel


class SelectOption(WizModel):
  def __init__(self, config: Dict):
    super().__init__(config)
