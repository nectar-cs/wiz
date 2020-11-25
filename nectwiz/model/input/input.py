from typing import Dict, List, Any

from nectwiz.core.core.types import KoD
from nectwiz.model.base.resource_selector import ResourceSelector
from nectwiz.model.base.wiz_model import WizModel


class GenericInput(WizModel):

  def serialize_options(self) -> List:
    from nectwiz.model.input.select_option import SelectOption
    option_models = self.inflate_children('options', SelectOption)
    return list(map(SelectOption.serialize, option_models))

  def extras(self) -> Dict[str, any]:
    return {}

  @staticmethod
  def sanitize_for_validation(value: Any) -> Any:
    return value
