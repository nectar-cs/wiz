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
    return self.load_children('field', Field)

  def operations(self):
    from wiz.model.operations.operation import Operation
    return self.load_children('operations', Operation)
