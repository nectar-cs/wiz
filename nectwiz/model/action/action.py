from typing import Dict

from nectwiz.core.core.types import ActionOutcome
from nectwiz.model.base.wiz_model import WizModel


class Action(WizModel):

  def final_status(self):
    pass

  def run(self, *args, **kwargs) -> ActionOutcome:
    try:
      outcome_bundle = self.perform(*args, **kwargs)
      return ActionOutcome(
        cls_name=self.__class__.__name__,
        id=self.id(),
        data=outcome_bundle,
        charge='positive'
      )
    except RuntimeError as err:
      return ActionOutcome(
        cls_name=self.__class__.__name__,
        id=self.id(),
        data=dict(error=str(err)),
        charge='negative'
      )

  def perform(self, *args, **kwargs) -> Dict:
    raise NotImplemented
