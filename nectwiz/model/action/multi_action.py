from typing import Dict, List

from nectwiz.model.action.action import Action
from nectwiz.model.action.observer import ReluctantObserver


class MultiAction(Action):

  def __init__(self, config: Dict):
    super().__init__(config)
    self.observer = ReluctantObserver()

  def load_sub_actions(self) -> List[Action]:
    return self.load_children('actions', Action)

  def perform(self, *args, **kwargs) -> Dict:
    sub_actions = self.load_sub_actions()

    combined_sub_items = []
    for action in sub_actions:
      combined_sub_items += action.observer.progress.get('sub_items', [])

    self.observer.progress['sub_items'] = combined_sub_items

    for action in sub_actions:
      action.observer.progress = self.observer.progress
      action.perform()

    return {}
