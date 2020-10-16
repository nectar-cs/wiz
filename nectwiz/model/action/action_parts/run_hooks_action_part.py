from typing import List

from nectwiz.core.core.types import ProgressItem
from nectwiz.model.action.base.observer import Observer
from nectwiz.model.hook.hook import Hook


class RunHookGroupActionPart:

  @staticmethod
  def progress_items(hooks: List[Hook]):
    items = []
    for index, hook in enumerate(hooks):
      action = hook.action()
      for sub_root in action.observer.progress['sub_items']:
        orig_title = sub_root.get('title')
        sub_root['title'] = f"Hook {index + 1}: {orig_title}"
        items.append(sub_root)
    return items

  @classmethod
  def perform(cls, observer: Observer, hooks: List[Hook]):
    for hook in hooks:
      action = hook.action()
      action.observer = observer
      action.run()
