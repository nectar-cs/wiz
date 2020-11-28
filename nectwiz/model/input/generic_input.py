from typing import Dict, List, Any, Optional
from werkzeug.utils import cached_property
from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.input.select_option import InputOption


class GenericInput(WizModel):

  KEY_OPTIONS = 'options'

  @cached_property
  def option_models(self):

    return self.inflate_children(
      InputOption,
      prop=self.KEY_OPTIONS
    )

  def compute_inferred_default(self) -> Optional[Any]:
    _serialized_options = self.serialize_options()
    if len(_serialized_options) > 0:
      return _serialized_options[0].get('id')
    return None

  def serialize_options(self) -> List:
    return list(map(InputOption.serialize, self.option_models))

  def extras(self) -> Dict[str, any]:
    return {}

  @staticmethod
  def sanitize_for_validation(value: Any) -> Any:
    return value
