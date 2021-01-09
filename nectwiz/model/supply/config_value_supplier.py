from typing import Any
from werkzeug.utils import cached_property
from nectwiz.core.core.config_man import config_man
from nectwiz.model.supply.value_supplier import ValueSupplier


class ConfigValueSupplier(ValueSupplier):

  KEY_FIELD_KEY = 'field_key'

  @cached_property
  def field_key(self) -> str:
    return self.get_prop(self.KEY_FIELD_KEY)

  def _compute(self) -> Any:
    return config_man.read_dict(self.field_key)
