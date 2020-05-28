from typing import Optional, List

from wiz.core import tedi_client
from wiz.model.base.wiz_model import WizModel


class ChartVariable(WizModel):

  def is_safe_to_set(self):
    explicit = self.config.get('safe')
    if explicit is not None:
      return str(explicit).lower() == 'true'
    else:
      return len(self.config.get('operations', [])) == 0

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

  def operations(self):
    from wiz.model.operations.operation import Operation
    return self.load_children('operations', Operation)
