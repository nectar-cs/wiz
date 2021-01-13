from typing import List, Any

from werkzeug.utils import cached_property

from nectwiz.model.action.base.action import Action


class MultiAction(Action):

  SUB_ACTIONS_KEY = 'sub_actions'

  @cached_property
  def sub_actions(self) -> List[Action]:
    return self.inflate_children(Action, prop=self.SUB_ACTIONS_KEY)

  def perform(self, **kwargs) -> Any:
    self.rewire_observers()
    did_fail = False
    for sub_action in self.sub_actions:
      result = sub_action.perform()
      if not result:
        did_fail = True
    return not did_fail

  def rewire_observers(self):
    for sub_action in self.sub_actions:
      progress_items = sub_action.observer.progress.get('sub_items', [])
      self.observer.progress['sub_items'] += progress_items
      sub_action.observer = self.observer
