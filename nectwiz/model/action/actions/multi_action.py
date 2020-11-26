from typing import List, Any

from werkzeug.utils import cached_property

from nectwiz.model.action.base.action import Action


class MultiAction(Action):

  SUB_ACTIONS_KEY = 'sub_actions'

  @cached_property
  def sub_actions(self) -> List[Action]:
    return self.inflate_children(Action, prop=self.SUB_ACTIONS_KEY)

  def rewire_observers(self):
    for sub_action in self.sub_actions:
      sub_action_progress = sub_action.observer.progress
      sub_action_progress_items = sub_action_progress.get('sub_items', [])
      self.observer.progress['sub_items'] += sub_action_progress_items

  def run(self, **kwargs) -> Any:
    self.rewire_observers()
    for sub_action in self.sub_actions:
      sub_action.observer.progress = self.observer.progress
      exec_outcome = sub_action.run(**kwargs)
      if not exec_outcome:
        return False
    return True
