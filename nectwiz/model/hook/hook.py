from typing import List, TypeVar, Dict

from nectwiz.model.action.action import Action
from nectwiz.model.base.wiz_model import WizModel


T = TypeVar('T', bound='Hook')

class Hook(WizModel):

  def __init__(self, config):
    super().__init__(config)
    self.action_desc = config.get('action')
    self.trigger_labels: Dict = config.get('triggerLabels', {})

  def subscribes_to(self, **labels) -> bool:
    return self.trigger_labels.items() <= labels.items()

  def action(self) -> Action:
    return super().load_child(Action, self.action_desc)

  @classmethod
  def by_trigger(cls, **labels) -> List[T]:
    all_hooks = cls.inflate_all()
    filterer = lambda hook: hook.subscribes_to(**labels)
    return list(filter(filterer, all_hooks))
