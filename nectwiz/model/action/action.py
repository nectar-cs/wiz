from nectwiz.core.core.types import ActionOutcome
from nectwiz.model.base.wiz_model import WizModel


class Action(WizModel):

  def final_status(self):
    pass


  def perform(self, *args, **kwargs) -> ActionOutcome:
    raise NotImplemented


