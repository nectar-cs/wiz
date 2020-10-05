from typing import Dict

from nectwiz.core.core.types import KoD
from nectwiz.model.base.wiz_model import WizModel


class ErrorDiagnosis(WizModel):
  def __init__(self, config: Dict):
    super().__init__(config)
    self.selector_kod: KoD = config.get('trigger_selector')
