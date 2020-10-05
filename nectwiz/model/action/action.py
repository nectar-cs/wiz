from typing import Dict

from nectwiz.model.action.action_observer import ActionObserver
from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.error.controller_error import MyErr


class Action(WizModel):
  def __init__(self, config: Dict):
    super().__init__(config)
    self.observer = ActionObserver()

  def run(self, **kwargs):
    try:
      self.perform(**kwargs)
    except MyErr as err:
      print(f"CAUGHT MY ERR {err.errdict}")
      self.observer.on_failed(err.errdict)

  def perform(self, *args, **kwargs) -> Dict:
    raise NotImplemented
