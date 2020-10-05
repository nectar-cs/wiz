from typing import List, Optional

from nectwiz.core.core.types import ErrDict


class ActionErrorsMan:
  def __init__(self):
    self.errors: List[ErrDict] = []

  def push_error(self, errdict: ErrDict):
    self.errors.append(errdict)

  def find_error(self, error_id: str) -> Optional[ErrDict]:
    finder = lambda errdict: errdict.get('uuid') == error_id
    return next(filter(finder, self.errors), None)


errors_man = ActionErrorsMan()
