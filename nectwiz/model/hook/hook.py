from typing import List

from nectwiz.model.action.action import Action
from nectwiz.model.base.wiz_model import WizModel


class Hook(WizModel):

  def actions(self) -> List[Action]:
    return super().load_children('actions', Action)

  def execute_async(self):
    func = self.__class__.execute_sync

  def execute_sync(self):
    outcomes = {}
    for action in self.actions():
      outcome = action.perform()
      outcomes[action.key] = outcome
    return outcomes
