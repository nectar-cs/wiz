from typing import List, Dict

from werkzeug.utils import cached_property

from nectwiz.model.action.actions.run_predicates_action import RunPredicatesAction
from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.predicate.predicate import Predicate


class SystemCheck(WizModel):

  PREDICATES_KEY = 'predicates'

  @classmethod
  def singleton_id(cls):
    return 'nectar.system-check'

  @cached_property
  def predicates(self) -> List[Predicate]:
    print(f"MY RAW IS {self.config.get(self.PREDICATES_KEY)}")
    return self.inflate_children(Predicate, prop=self.PREDICATES_KEY)

  def multi_predicate_action_config(self) -> Dict:
    return dict(
      kind=RunPredicatesAction.__name__,
      predicates=self.config.get(self.PREDICATES_KEY, []),
      event_type='system_check',
      store_telem=True
    )

  def is_non_empty(self) -> bool:
    return len(self.predicates) > 0
