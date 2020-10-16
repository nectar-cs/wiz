from typing import List

from nectwiz.core.core.types import ProgressItem
from nectwiz.model.action.base.observer import Observer
from nectwiz.model.hook.hook import Hook


class RunHookGroupActionPart:

  @staticmethod
  def progress_items(which: str, hooks: List[Hook]):
    items = []
    for index, hook in enumerate(hooks):
      action = hook.action()
      for action_progress_item in action.observer.progress['sub_items']:
        orig_title = action_progress_item.get('title')
        prefix = f"{which.title()} Hook {index + 1}"
        action_progress_item['title'] = f"{prefix}: {orig_title}"
        items.append(action_progress_item)
    return items

  @classmethod
  def perform(cls, observer: Observer, hooks: List[Hook]):
    for hook in hooks:
      action = hook.action()
      action.observer = observer
      action.run()
