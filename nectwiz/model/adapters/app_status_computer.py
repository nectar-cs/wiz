from werkzeug.utils import cached_property

from nectwiz.core.core.config_man import config_man
from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.predicate.common_predicates import FalsePredicate
from nectwiz.model.predicate.predicate import Predicate


class AppStatusComputer(WizModel):

  STATUS_RUNNING = 'running'
  STATUS_BROKEN = 'broken'
  PREDICATE_KEY = 'predicate'

  @classmethod
  def singleton_id(cls):
    return 'nectar.app-status-computer'

  @cached_property
  def predicate(self) -> Predicate:
    return self.inflate_child(
      Predicate,
      prop=self.PREDICATE_KEY,
      safely=True
    ) or self.inflate_child(Predicate, kod=FalsePredicate.__name__)

  def compute_status(self) -> str:
    eval_result = self.predicate.evaluate()
    return self.STATUS_RUNNING if eval_result else self.STATUS_BROKEN

  def compute_and_commit_status(self) -> str:
    status = self.compute_status()
    config_man.write_application_status(status)
    return status
