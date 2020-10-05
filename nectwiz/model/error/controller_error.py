from nectwiz.core.core.types import KAOs, ErrDict
from nectwiz.model.operation.step_state import StepState


class MyErr(Exception):
  def __init__(self, errdict: ErrDict):
    super().__init__('def')
    self.errdict = errdict


