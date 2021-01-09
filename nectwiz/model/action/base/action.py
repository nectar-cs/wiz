import traceback
from datetime import datetime
from typing import Dict, Any

import inflection
from werkzeug.utils import cached_property

from nectwiz.core.core import utils
from nectwiz.core.telem import telem_man
from nectwiz.model.action.base.observer import Observer
from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.error.controller_error import ActionHalt


class Action(WizModel):

  KEY_EVENT_ID = 'event_id'
  KEY_STORE_TELEM = 'store_telem'
  KEY_EVENT_TYPE = 'event_type'
  KEY_EVENT_NAME = 'event_name'
  KEY_HALT_ON_EXEC = 'treat_exception_as_fatal'
  KEY_TELEM_EXTRAS = 'telem_extras'

  def __init__(self, config: Dict):
    super().__init__(config)
    self.observer = Observer()
    self.outcome = None

  @cached_property
  def event_id(self) -> str:
    return self.get_prop(self.KEY_EVENT_ID)

  @cached_property
  def store_telem(self) -> bool:
    return self.get_prop(self.KEY_STORE_TELEM, False)

  @cached_property
  def event_type(self) -> str:
    return self.get_prop(
      self.KEY_EVENT_TYPE,
      inflection.underscore(self.__class__.__name__)
    )

  @cached_property
  def event_name(self) -> str:
    return self.get_prop(self.KEY_EVENT_NAME)

  @cached_property
  def halt_on_exception(self) -> bool:
    return self.get_prop(self.KEY_HALT_ON_EXEC, True)

  @cached_property
  def static_telem_extras(self) -> Dict:
    return self.get_prop(self.KEY_TELEM_EXTRAS, {})

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
        type='internal_error',
        fatal=self.halt_on_exception,
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
