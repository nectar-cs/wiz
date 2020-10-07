import traceback
from typing import Dict, Any

from nectwiz.model.action.base.observer import Observer
from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.error.controller_error import ActionHalt


class Action(WizModel):
  def __init__(self, config: Dict):
    super().__init__(config)
    self.observer = Observer()

  def run(self, **kwargs) -> Any:
    try:
      return self.perform(**kwargs)
    except ActionHalt as err:
      print(f"CAUGHT MY ERR {err.errdict}")
      self.observer.on_failed(err.errdict)
      return False
    except Exception as err:
      print(f"[nectwiz::action] fatal uncaught exception {err}")
      print(traceback.format_exc())
      return False

  def perform(self, *args, **kwargs) -> Dict:
    raise NotImplemented
