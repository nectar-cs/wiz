from typing import List, TypeVar, Dict

from nectwiz.model.action.action import Action
from nectwiz.model.base.wiz_model import WizModel


T = TypeVar('T', bound='Hook')

class Hook(WizModel):

  def __init__(self, config):
    super().__init__(config)
    self.action_desc = config.get('action')
    self.trigger_selector: Dict = config.get('trigger_selector') or {}
    self.abort_on_fail: bool = config.get('abort_on_fail', False)

  def subscribes_to(self, **labels) -> bool:
    selector_items = self.trigger_selector.items()
    if len(selector_items) > 0:
      return selector_items <= labels.items()
    else:
      return False

  def action(self) -> Action:
    return super().load_child(Action, self.action_desc)

  def run(self):
    return self.action().run()

  @classmethod
  def by_trigger(cls, **labels) -> List[T]:
    all_hooks = cls.inflate_all()
    filterer = lambda hook: hook.subscribes_to(**labels)
    return list(filter(filterer, all_hooks))
