from typing import List, TypeVar

from nectwiz.model.action.action import Action
from nectwiz.model.base.wiz_model import WizModel


T = TypeVar('T', bound='Hook')

class Hook(WizModel):

  def __init__(self, config):
    super().__init__(config)
    self.trigger: str = config.get('trigger')

  @property
  def event(self):
    return self.trigger.split('::')[1]

  @property
  def timing(self):
    return self.trigger.split('::')[0]

  def subscribes_to(self, event: str, timing: str) -> bool:
    return self.event == event and self.timing == timing

  def actions(self) -> List[Action]:
    return super().load_children('actions', Action)

  def execute_async(self):
    func = self.__class__.execute_sync

  def execute_sync(self):
    outcomes = {}
    for action in self.actions():
      outcome = action.perform()
      outcomes[action.id()] = outcome
    return outcomes

  @classmethod
  def list_for_trigger(cls, what: str, when: str) -> List[T]:
    all_hooks = cls.inflate_all()
    filterer = lambda hook: hook.subscribes_to(what, when)
    return list(filter(filterer, all_hooks))
