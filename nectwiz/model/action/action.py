from typing import Dict

from nectwiz.core.core.types import ActionOutcome
from nectwiz.model.action.observer import Observer
from nectwiz.model.base.wiz_model import WizModel


class Action(WizModel):

  def __init__(self, config: Dict):
    super().__init__(config)
    self.observer = Observer()

  def final_status(self):
    pass

  def run(self, **kwargs) -> ActionOutcome:
    try:
      outcome_bundle = self.perform(**kwargs)
      return ActionOutcome(
        cls_name=self.__class__.__name__,
        id=self.id(),
        data=outcome_bundle,
        charge='positive'
      )
    except Exception as err:
      print("ACTION ERR")
      print(err)
      return ActionOutcome(
        cls_name=self.__class__.__name__,
        id=self.id(),
        data=dict(error=str(err)),
        charge='negative'
      )

  def perform(self, *args, **kwargs) -> Dict:
    raise NotImplemented
