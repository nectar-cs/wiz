import traceback
from datetime import datetime
from typing import Dict, Any

from nectwiz.core.core import utils
from nectwiz.core.telem import telem_man
from nectwiz.model.action.base.observer import Observer
from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.error.controller_error import ActionHalt


class Action(WizModel):
  def __init__(self, config: Dict):
    super().__init__(config)
    self.observer = Observer()
    self.event_id = config.get('event_id')
    self.store_telem = config.get('store_telem', False)
    self.event_type = config.get('event_type', self.__class__.__name__)
    self.outcome = None

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
        fatal=False,
        tone='error',
        reason='Internal error',
        logs=[traceback.format_exc()]
      )
      self.outcome = False
    finally:
      if telem_man.is_on():
        event_id = self.event_id
        if self.store_telem:
          print(f"[nectwiz::action] {self.id()} self-storing telem[{event_id}]")
          stored_event = telem_man.store_event(dict(
            _id=event_id or utils.rand_str(20),
            event_type=self.event_type,
            occurred_at=str(datetime.now())
          ))
          event_id = stored_event['_id']
        else:
          print(f"[nectwiz::action] SKIP {self.id()} self-storing telem[{event_id}]")

        for error in self.observer.errdicts:
          error['event_id'] = event_id
          telem_man.store_error(error)

      return self.outcome

  def perform(self, *args, **kwargs) -> bool:
    raise NotImplemented
