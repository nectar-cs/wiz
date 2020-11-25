from typing import List, Dict

from nectwiz.core.core.types import KoD
from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.operation.operation_state import OperationState
from nectwiz.model.action.actions.run_predicates_action import RunPredicatesAction
from nectwiz.model.predicate.predicate import Predicate
from nectwiz.model.operation.stage import Stage


class Operation(WizModel):

  def __init__(self, config: Dict):
    super().__init__(config)
    self.synopsis: str = self.asset_attr(config.get('synopsis'))
    self.is_system: bool = self.id() in ['installation', 'uninstall']
    self.preflight_descs: List[KoD] = config.get('preflight_predicates', [])

  def preflight_action_config(self) -> Dict:
    return dict(
      kind=RunPredicatesAction.__name__,
      predicates=self.preflight_descs
    )

  def has_preflight_checks(self) -> bool:
    return len(self.preflight_descs) > 0

  def stages(self) -> List[Stage]:
    """
    Loads the Stages associated with the Operation.
    :return: list of Stage instances.
    """
    return self.inflate_children('stages', Stage)

  def stage(self, key) -> Stage:
    """
    Finds the Stage by key and inflates (instantiates) into a Stage instance.
    :param key: identifier for desired Stage.
    :return: Stage instance.
    """
    return self.inflate_child_in_list('stages', Stage, key)
