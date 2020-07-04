from wiz.model.base.wiz_model import WizModel


class ExitCondition(WizModel):

  @property
  def cond_type(self):
    return self.config.get('type')

  def evaluate(self):




