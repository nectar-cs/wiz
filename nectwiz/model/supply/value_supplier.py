from functools import lru_cache
from typing import Any, Dict, Union, Optional

from nectwiz.model.base.wiz_model import WizModel


class ValueSupplier(WizModel):

  def __init__(self, config: Dict):
    super().__init__(config)
    self.treat_as_list = self.get_prop('many', None)
    self.desired_output_format = self.get_prop('output', None)

  def produce(self) -> Any:
    computed_value = self._compute()
    return self.serialize_computed_value(computed_value)

  def serialize_computed_value(self, computed_value) -> Any:
    treat_as_list = self.treat_as_list
    if treat_as_list in [None, 'auto']:
      treat_as_list = type(computed_value) == list

    if treat_as_list:
      if type(computed_value) == list:
        return [self.serialize_item(item) for item in computed_value]
      else:
        return [self.serialize_item(computed_value)]
    else:
      if not type(computed_value) == list:
        return self.serialize_item(computed_value)
      else:
        item = computed_value[0] if len(computed_value) > 0 else None
        return self.serialize_item(item) if item else None

  @lru_cache(maxsize=1)
  def output_format(self) -> Union[Dict, str]:
    return self.desired_output_format

  def _compute(self) -> Any:
    raise NotImplementedError

  def serialize_item(self, item: Any) -> Union[Dict, str]:
    fmt = self.output_format()
    if not fmt or type(fmt) == str:
      return self.serialize_item_prop(item, fmt)
    elif type(fmt) == dict:
      return self.serialize_dict_item(item)
    else:
      return ''

  def serialize_dict_item(self, item):
    fmt: Dict = self.output_format()
    serialized = {}
    for key, value in list(fmt.items()):
      serialized[key] = self.serialize_item_prop(item, value)
    return serialized

  @staticmethod
  def serialize_item_prop(item: Any, prop_name: Optional[str]) -> Optional[Any]:
    if prop_name:
      if item:
        if type(item) == dict:
          return item.get(prop_name)
        else:
          # noinspection PyBroadException
          try:
            attr = getattr(item, prop_name)
            return attr() if callable(attr) else attr
          except:
            return None
      else:
        return None
    else:
      return item
