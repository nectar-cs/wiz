import traceback
from datetime import datetime
from typing import Dict, Any

import inflection

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
    self.static_telem_extras = config.get('telem_extras', {})
    self.store_telem = config.get('store_telem', False)
    self.event_type = config.get(
      'event_type',
      inflection.underscore(self.__class__.__name__)
    )
    self.event_name = config.get('event_name')
    self.outcome = None
    self.halt_on_exc = config.get('treat_exception_as_fatal', True)

  def run(self, **kwargs) -> Any:
    try:
      self.outcome = self.perform(**kwargs)
    except ActionHalt as err:
      print(f"[nectwiz::action] controlled err halt signal {err.errdict}")
      self.observer.on_failed()
      self.outcome = False
    except Exception as err:
      print(f"[nectwiz::action] fatal uncaught exception {err}")
      print(traceback.format_exc())
      self.observer.process_error(
        id='internal-error',
        type='internal_error',
        fatal=self.halt_on_exc,
        tone='error',
        reason='Internal error',
        logs=[traceback.format_exc()]
      )
      self.outcome = False
    finally:
      # noinspection PyBroadException
      try:
        self.handle_telem()
      except:
        print("[nectwiz::action] telem handling failed")
        print(traceback.format_exc())
      return self.outcome

  def handle_telem(self):
    if telem_man.is_storage_ready():
      event_id = self.event_id
      if self.store_telem:
        print(f"[nectwiz::action] danger event_id and store_event")
        event_bundle = self.gen_own_telem_bundle(event_id)
        insertion_result = telem_man.store_event(event_bundle)
        event_id = str(insertion_result.inserted_id)
      else:
        print(f"[nectwiz::action] SKIP {self.id()} self-storing telem[{event_id}]")
      for error in self.observer.errdicts:
        error['event_id'] = event_id
        telem_man.store_error(error)

  def gen_own_telem_bundle(self, event_id):
    return dict(
      _id=event_id or utils.rand_str(20),
      type=self.event_type,
      name=self.event_name,
      status='positive' if self.outcome else 'negative',
      extras=self.telem_extras(),
      occurred_at=str(datetime.now())
    )

  def perform(self, **kwargs) -> bool:
    raise NotImplemented

  def telem_extras(self) -> Dict:
    return self.static_telem_extras
