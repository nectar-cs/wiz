from typing import Dict

from nectwiz.model.action.action import Action


class FlushTelemAction(Action):
  
  def __init__(self, config):
    super().__init__(config)
  
  def perform(self) -> Dict:
    # metric = telem_sync.upload_operation_outcomes()
    print("I AM ACTION")
    return {}
