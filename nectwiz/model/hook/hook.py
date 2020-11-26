from typing import List, TypeVar, Dict, Any

from werkzeug.utils import cached_property

from nectwiz.model.action.base.action import Action
from nectwiz.model.base.wiz_model import WizModel


T = TypeVar('T', bound='Hook')

class Hook(WizModel):

  ACTION_KEY = 'action'
  TRIGGER_SELECTOR_KEY = 'trigger_selector'

  @cached_property
  def action(self) -> Action:
    return self.inflate_child(Action, prop=self.ACTION_KEY)

  @cached_property
  def trigger_selector(self) -> Dict:
    return self.get_prop(self.TRIGGER_SELECTOR_KEY) or {}

  def run(self) -> Any:
    return self.action.run()

  def subscribes_to(self, **labels) -> bool:
    selector_items = self.trigger_selector.items()
    if len(selector_items) > 0:
      return selector_items <= labels.items()
    else:
      return False

  @classmethod
  def by_trigger(cls, **labels) -> List[T]:
    all_hooks = cls.inflate_all()
    filterer = lambda hook: hook.subscribes_to(**labels)
    return list(filter(filterer, all_hooks))
