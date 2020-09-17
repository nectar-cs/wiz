from typing import Dict, List, Optional

from nectwiz.core.core.config_man import config_man
from nectwiz.core.core.utils import deep_get
from nectwiz.model.base.wiz_model import WizModel


class Input(WizModel):

  def __init__(self, config: Dict):
    super().__init__(config)
    self.option_descs = config.get('options')
    self.provider_desc = config.get('options_provider')
    self.expl_default = config.get('default')

  def type(self):
    return self.__class__.__name__

  def default_value(self) -> Optional[str]:
    if self.expl_default:
      return self.expl_default
    else:
      variable_id = self.parent and self.parent.id()
      if variable_id:
        tam_defaults = config_man.tam_defaults() or {}
        return deep_get(tam_defaults, self.id().split("."))
      else:
        return self.implied_default()

  def implied_default(self) -> Optional[str]:
    return None

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
    provider = WizModel.inflate(self.provider_desc)
    return provider.as_options()
