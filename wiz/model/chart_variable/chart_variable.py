from typing import Optional, List

from wiz.core import tedi_client
from wiz.model.base.wiz_model import WizModel


class ChartVariable(WizModel):

  @property
  def data_type(self):
    return self.config.get('type', 'string')

  @property
  def is_ephemeral(self):
    return self.config.get('ephemeral', False)

  @property
  def default_value(self):
    return self.config.get('default')

  @property
  def linked_res_name(self):
    return self.config.get('resource')

  @property
  def mode(self):
    return self.config.get('mode', 'internal')

  @property
  def category(self):
    return self.config.get('category')

  def is_safe_to_set(self):
    return self.mode == 'public'

  def field(self):
    from wiz.model.field.field import Field
    children = self.load_children('field', Field)
    return children[0] if len(children) == 1 else None

  def validate(self, value) -> List[Optional[str]]:
    from wiz.model.field.field import Field
    field: Field = self.field()
    if field:
      return field.validate(value)
    else:
      return [None, None]

  def read_crt_value(self, cache=None) -> Optional[str]:
    if cache is not None:
      return tedi_client.deep_get(cache, self.key.split('.'))
    else:
      return tedi_client.chart_value(self.key)

  def commit(self, value):
    tedi_client.commit_values([(self.key, value)])
    if self.is_safe_to_set():
      tedi_client.apply(rules=None, inlines=None)

  def operations(self):
    from wiz.model.operations.operation import Operation
    return self.load_children('operations', Operation)
