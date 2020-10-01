from typing import List, Dict

from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.operation.operation_state import OperationState
from nectwiz.model.pre_built.run_predicates_action import RunPredicatesAction
from nectwiz.model.predicate.predicate import Predicate
from nectwiz.model.operation.stage import Stage


class Operation(WizModel):

  def __init__(self, config: Dict):
    super().__init__(config)
    self.synopsis: str = self.asset_attr(config.get('synopsis'))
    self.is_system: bool = self.id() in ['installation', 'uninstall']

  def preflight_action_config(self) -> Dict:
    return dict(
      kind=RunPredicatesAction.__name__,
      predicates=self.config.get('preflight_predicates', [])
    )

  def is_state_owner(self, op_state: OperationState) -> bool:
    """
    Checks if the passed OperationState belongs to current operation.
    :param op_state: OperationState instance.
    :return: True if belongs, False otherwise.
    """
    return op_state.op_id == self.id()

  def stages(self) -> List[Stage]:
    """
    Loads the Stages associated with the Operation.
    :return: list of Stage instances.
    """
    return self.load_children('stages', Stage)

  def stage(self, key) -> Stage:
    """
    Finds the Stage by key and inflates (instantiates) into a Stage instance.
    :param key: identifier for desired Stage.
    :return: Stage instance.
    """
    return self.load_list_child('stages', Stage, key)

  def preflight_predicates(self) -> List[Predicate]:
    """
    Loads the Prerequisites associated with the Operation.
    :return: list of Predicate instances.
    """
    return self.load_children('preflight', Predicate)
