from typing import List, Dict

from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.operation.operation_state import OperationState
from nectwiz.model.pre_built.run_predicates_action import RunPredicatesAction
from nectwiz.model.predicate.predicate import Predicate
from nectwiz.model.stage.stage import Stage


class Operation(WizModel):

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

  @classmethod
  def find_own_state(cls, op_states: List[OperationState]):
    """
    Finds the current State of the Operation.
    :param op_states: list of candidate Operation States to be filtered.
    :return: OperationState instance.
    """
    return next(filter(cls.is_state_owner, op_states))

  @property
  def is_system(self) -> bool:
    """
    Checks if a given operation is classified as a system type.
    :return: True if successful, False otherwise.
    """
    return self.id() in ['installation', 'uninstall']

  @property
  def synopsis(self) -> List[str]:
    """
    Getter for the synopsis property. Defaults to empty list if absent.
    :return: synopsis.
    """
    return self.config.get('synopsis', [])

  @property
  def long_desc(self) -> str:
    """
    Getter for the long description property. Defaults to empty string if absent.
    :return: long description.
    """
    return self.config.get('description', '')

  @property
  def risks(self) -> List[str]:
    """
    Getter for the risks property. Defaults to empty list if absent.
    :return: list of risks.
    """
    return self.config.get('risks', [])

  @property
  def affects_data(self):
    """
    Getter for the affects data property. Defaults to False if absent.
    :return: affects data.
    """
    return self.config.get('affects_data', False)

  @property
  def affects_uptime(self):
    """
    Getter for the affects uptime property. Defaults to False if absent.
    :return: affects uptime.
    """
    return self.config.get('affects_uptime', False)

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

  def preflight_predicate(self, key: str) -> Predicate:
    """
    Finds the Prerequisite by key and inflates (instantiates) into a Predicate
    instance.
    :param key: identifier for desired Prerequisite.
    :return: Predicate instance.
    """
    return self.load_list_child('preflight', Predicate, key)
