from typing import Dict

from nectwiz.core.core import updates_man
from nectwiz.core.core.types import ProgressItem
from nectwiz.model.action.action_parts.run_hooks_action_part import RunHookGroupActionPart
from nectwiz.model.action.base.action import Action


class RunUpdateHooksAction(Action):
  def __init__(self, config: Dict):
    super().__init__(config)
    self.timing = config['when']
    self.store_telem = True
    self.event_type = f'{self.timing}_update_hook'
    self.observer.progress = ProgressItem(
      id=f'wiz-{self.timing}-update-action',
      status='running',
      info=f"Runs {self.timing}-installation hooks",
      sub_items=[]
    )

  def perform(self):
    hooks = updates_man.find_hooks(self.timing, 'wiz_update')
    progress_items = RunHookGroupActionPart.progress_items(self.timing, hooks)
    self.observer.progress['sub_items'] = progress_items
    RunHookGroupActionPart.perform(self.observer, hooks)
    return True


