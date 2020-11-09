import traceback
from typing import Dict

from nectwiz.core.core.config_man import config_man
from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.predicate.predicate import Predicate


class AppStatusComputer(WizModel):

  def __init__(self, config: Dict):
    super().__init__(config)
    self.predicate_desc = config.get('predicate')

  @classmethod
  def singleton_id(cls):
    return 'nectar.app-status-computer'

  def compute_status(self) -> str:
    # noinspection PyBroadException
    try:
      predicate = self.load_child(Predicate, self.predicate_desc)
      eval_result = predicate.evaluate({})
      return 'running' if eval_result else 'broken'
    except:
      print("[nectwiz:app_status_computer] no predicate or override!")
      print(traceback.format_exc())
      return 'error'

  def compute_and_commit_status(self) -> str:
    status = self.compute_status()
    config_man.write_application_status(status)
    return status
