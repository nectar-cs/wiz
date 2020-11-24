from typing import Dict, List, Any

from nectwiz.model.action.base.action import Action


class MultiAction(Action):

  def __init__(self, config: Dict):
    super().__init__(config)
    self.sub_actions: List[Action] = self.inflate_children(
      'sub_actions',
      Action
    )

    for sub_action in self.sub_actions:
      sub_action_progress = sub_action.observer.progress
      sub_action_progress_items = sub_action_progress.get('sub_items', [])
      self.observer.progress['sub_items'] += sub_action_progress_items

  def run(self, **kwargs) -> Any:
    for sub_action in self.sub_actions:
      sub_action.observer.progress = self.observer.progress
      exec_outcome = sub_action.run(**kwargs)
      if not exec_outcome:
        return False
    return True
