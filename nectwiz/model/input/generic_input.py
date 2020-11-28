from typing import Dict, List, Any

from werkzeug.utils import cached_property

from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.input.select_option import SelectOption


class GenericInput(WizModel):

  KEY_OPTIONS = 'options'

  @cached_property
  def option_models(self):
    return self.inflate_children(
      SelectOption,
      prop=self.KEY_OPTIONS
    )

  def serialize_options(self) -> List:
    return list(map(SelectOption.serialize, self.option_models))

  def extras(self) -> Dict[str, any]:
    return {}

  @staticmethod
  def sanitize_for_validation(value: Any) -> Any:
    return value
