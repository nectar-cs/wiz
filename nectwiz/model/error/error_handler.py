from typing import Dict

from nectwiz.core.core.types import KoD
from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.error.error_context import ErrCtx
from nectwiz.model.error.error_trigger_selector import ErrorTriggerSelector


class ErrorHandler(WizModel):
  def __init__(self, config: Dict):
    super().__init__(config)
    self.selector_kod: KoD = config.get('trigger_selector')

  def match_confidence_score(self, err_cont: ErrCtx):
    trigger_selector = ErrorTriggerSelector.inflate(self.selector_kod)
    if trigger_selector:
      return trigger_selector.match_confidence_score(err_cont)
    else:
      return 0
