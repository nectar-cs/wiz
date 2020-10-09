from typing import Dict, List

from nectwiz.model.action.base.action import Action


class MultiAction(Action):

  def __init__(self, config: Dict):
    super().__init__(config)
    # self.observer = ReluctantObserver()

  def load_sub_actions(self) -> List[Action]:
    return self.inflate_children('sub_actions', Action)

  def perform(self, *args, **kwargs) -> Dict:
    for action in self.load_sub_actions():
      static_subs = action.observer.progress.get('sub_items', [])
      self.observer.progress['sub_items'] += static_subs
      action.observer.progress = self.observer.progress
      action.perform()
    return {}
