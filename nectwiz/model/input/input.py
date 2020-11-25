from typing import Dict, List, Any

from nectwiz.model.base.resource_selector import ResourceSelector
from nectwiz.model.base.wiz_model import WizModel


class GenericInput(WizModel):

  def __init__(self, config: Dict):
    super().__init__(config)
    self.option_descs = config.get('options')

  def options_list(self) -> List:
    if self.provider_desc:
      return self.load_provider_options()
    else:
      return self.load_options()

  def extras(self) -> Dict[str, any]:
    return {}

  def load_options(self) -> List:
    return []

  @staticmethod
  def sanitize_for_validation(value: Any) -> Any:
    return value
