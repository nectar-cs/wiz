from typing import List

from nectwiz.model.base.wiz_model import WizModel, key_or_dict_to_key
from nectwiz.model.operation.operation_state import OperationState
from nectwiz.model.predicate.predicate import Predicate
from nectwiz.model.stage.stage import Stage


class Operation(WizModel):

  def first_stage_key(self) -> str:
    """
    Returns the key of the first associated Stage, if present.
    :return: Stage key if present, else None.
    """
    stage_descriptors = self.config.get('stages', [])
    first = stage_descriptors[0] if len(stage_descriptors) else 0
    return key_or_dict_to_key(first) if first else None

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

  def prerequisites(self) -> List[Predicate]:
    """
    Loads the Prerequisites associated with the Operation.
    :return: list of Predicate instances.
    """
    return self.load_children('prerequisites', Predicate)

  def prerequisite(self, key:str) -> Predicate:
    """
    Finds the Prerequisite by key and inflates (instantiates) into a Predicate
    instance.
    :param key: identifier for desired Prerequisite.
    :return: Predicate instance.
    """
    return self.load_list_child('prerequisites', Predicate, key)