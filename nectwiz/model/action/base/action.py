import json
import traceback
from typing import Dict, Any

from rq import get_current_job

from nectwiz.core.telem import telem_man
from nectwiz.model.action.base.observer import Observer
from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.error.controller_error import ActionHalt


class Action(WizModel):
  def __init__(self, config: Dict):
    super().__init__(config)
    self.observer = Observer()
    self.outcome = None
    self.record_own_telem: bool = config.get('handle_telem')

  def run(self, **kwargs) -> Any:
    try:
      self.outcome = self.perform(**kwargs)
    except ActionHalt as err:
      print(f"[nectwiz::action] controlled failure halt sig {err.errdict}")
      self.observer.on_failed()
      self.outcome = False
    except Exception as err:
      print(f"[nectwiz::action] fatal uncaught exception {err}")
      print(traceback.format_exc())
      self.observer.process_error(
        id='internal-error',
        fatal=True,
        reason='Internal error',
        logs=[traceback.format_exc()]
      )
      self.outcome = False
    finally:
      if self.record_own_telem:
        telem_man.store_outcome(self.telem_bundle())
      else:
        job = get_current_job()
        if job:
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
