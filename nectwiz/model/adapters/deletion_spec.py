from nectwiz.model.base.wiz_model import WizModel


class DeletionSpec(WizModel):
  def __init__(self, config):
    super().__init__(config)
    self.groups = config.get('victim_groups')
