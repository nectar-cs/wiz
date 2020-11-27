from typing import Any, Dict, Union, Optional

from werkzeug.utils import cached_property

from nectwiz.core.core import utils
from nectwiz.core.core.utils import listlike
from nectwiz.model.base.wiz_model import WizModel


class ValueSupplier(WizModel):

  IS_MANY_KEY = 'many'
  OUTPUT_FMT_KEY = 'output'

  @cached_property
  def treat_as_list(self):
    return self.get_prop(self.IS_MANY_KEY)

  @cached_property
  def output_format(self):
    return self.get_prop(self.OUTPUT_FMT_KEY)

  def resolve(self) -> Any:
    computed_value = self._compute()
    return self.serialize_computed_value(computed_value)

  def serialize_computed_value(self, computed_value) -> Any:
    treat_as_list = self.treat_as_list
    if treat_as_list in [None, 'auto']:
      treat_as_list = listlike(computed_value)

    if treat_as_list and not self.output_format == '__count__':
      if listlike(computed_value):
        return [self.serialize_item(item) for item in computed_value]
      else:
        return [self.serialize_item(computed_value)]
    else:
      if not listlike(computed_value) or self.output_format == '__count__':
        return self.serialize_item(computed_value)
      else:
        item = computed_value[0] if len(computed_value) > 0 else None
        return self.serialize_item(item) if item else None

  def _compute(self) -> Any:
    raise NotImplementedError

  def serialize_item(self, item: Any) -> Union[Dict, str]:
    fmt = self.output_format
    if not fmt or type(fmt) == str:
      return self.serialize_item_prop(item, fmt)
    elif type(fmt) == dict:
      return self.serialize_dict_item(item)
    else:
      return ''

  def serialize_dict_item(self, item):
    fmt: Dict = self.output_format
    serialized = {}
    for key, value in list(fmt.items()):
      serialized[key] = self.serialize_item_prop(item, value)
    return serialized

  # noinspection PyBroadException
  @staticmethod
  def serialize_item_prop(item: Any, prop_name: Optional[str]) -> Optional[Any]:
    if prop_name:
      if prop_name == '__count__':
        try:
          return len(item)
        except:
          return 0
      else:
        try:
          return utils.pluck_or_getattr_deep(item, prop_name)
        except:
          return None
    else:
      return item
