from typing import List, Dict

from nectwiz.model.action.actions.run_predicates_action import RunPredicatesAction
from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.predicate.predicate import Predicate


class SystemCheck(WizModel):

  def predicates(self) -> List[Predicate]:
    return self.inflate_children('predicates', Predicate)

  def multi_predicate_action_config(self) -> Dict:
    return dict(
      kind=RunPredicatesAction.__name__,
      predicates=self.config.get('predicates', []),
      event_type='system_check',
      store_telem=True
    )

  def is_non_empty(self) -> bool:
    return len(self.predicates()) > 0


master_syscheck_id = 'system-check'
