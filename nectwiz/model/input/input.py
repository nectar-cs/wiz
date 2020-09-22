from typing import Dict, List

from nectwiz.model.base.resource_selector import ResourceSelector
from nectwiz.model.base.wiz_model import WizModel


class GenericInput(WizModel):

  def __init__(self, config: Dict):
    super().__init__(config)
    self.option_descs = config.get('options')
    self.provider_desc = config.get('options_provider')

  def options(self) -> List:
    if self.provider_desc:
      return self.load_provider_options()
    else:
      return self.load_options()

  def extras(self) -> Dict[str, any]:
    return {}

  def load_options(self) -> List:
    return []

  def load_provider_options(self):
    provider = ResourceSelector.inflate(self.provider_desc)
    return provider.as_options()

  def requires_decoration(self) -> bool:
    return False
