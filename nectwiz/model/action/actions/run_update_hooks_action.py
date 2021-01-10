from typing import Dict

from werkzeug.utils import cached_property

from nectwiz.core.core import updates_man
from nectwiz.core.core.types import ProgressItem
from nectwiz.model.action.action_parts.run_hooks_action_part import RunHookGroupActionPart
from nectwiz.model.action.base.action import Action


class RunUpdateHooksAction(Action):
  def __init__(self, config: Dict):
    super().__init__(config)
    self.timing = config['when']
    self.observer.progress = ProgressItem(
      id=f'wiz-{self.timing}-update-action',
      status='running',
      info=f"Runs {self.timing}-installation hooks",
      sub_items=[]
    )

  @cached_property
  def store_telem(self) -> bool:
    return True

  def perform(self):
    hooks = updates_man.find_hooks(self.timing, 'wiz_update')
    progress_items = RunHookGroupActionPart.progress_items(self.timing, hooks)
    self.observer.progress['sub_items'] = progress_items
    RunHookGroupActionPart.perform(self.observer, hooks)
    return True
