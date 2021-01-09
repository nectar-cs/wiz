from typing import Dict

from nectwiz.core.core.types import ProgressItem
from nectwiz.model.action.base.action import Action


class ApplyUpdateAction(Action):
  def __init__(self, config: Dict):
    super().__init__(config)
    self.store_telem = True
    self.event_type = f'apply_update'
    self.observer.progress = ProgressItem(
      id=f'apply_update',
      status='running',
      info=f"Updates default values, re-applies manifest",
      sub_items=[]
    )

  def perform(self, **kwargs) -> bool:
    pass
