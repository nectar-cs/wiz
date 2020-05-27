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

  def validate(self, value):
    from wiz.model.field.field import Field
    field: Field = self.field()
    if field:
      return field.validate(value)
    else:
      return True

  def read_crt_value(self):
    return tedi_client.chart_values().get(self.key)

  def operations(self):
    from wiz.model.operations.operation import Operation
    return self.load_children('operations', Operation)
