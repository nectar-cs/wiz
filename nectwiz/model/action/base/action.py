import json
import traceback
from typing import Dict, Any

from rq import get_current_job

from nectwiz.model.action.base.observer import Observer
from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.error.controller_error import ActionHalt


class Action(WizModel):
  def __init__(self, config: Dict):
    super().__init__(config)
    self.observer = Observer()
    self.outcome = None

  def run(self, **kwargs) -> Any:
    try:
      self.outcome = self.perform(**kwargs)
    except ActionHalt as err:
      print(f"[nectwiz::action] halt sig {err.errdict}")
      self.observer.on_failed()
      self.outcome = False
    except Exception as err:
      print(f"[nectwiz::action] fatal uncaught exception {err}")
      print(traceback.format_exc())
      self.outcome = False
    finally:
      print(f"[nectwiz::action] {self.__class__.__name__} exit")
      job = get_current_job()
      if job:
        print(f"[nectwiz::action::exit] {self.telem_bundle()}")
        job.meta['telem'] = json.dumps(self.telem_bundle())
        job.save_meta()
      else:
        print(f"[nectwiz::action::exit] could not find own job!")
      return self.outcome

  def telem_bundle(self) -> Dict:
    try:
      progress = self.observer.progress
      if progress.get('status') is None:
        progress['status'] = 'positive' if self.outcome else 'negative'
      return dict(
        **progress,
        errdicts=self.observer.errdicts
      )
    except:
      print(traceback.format_exc())
      return {}

  def perform(self, *args, **kwargs) -> Dict:
    raise NotImplemented
