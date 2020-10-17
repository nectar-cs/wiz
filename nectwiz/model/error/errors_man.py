from typing import List, Optional

from nectwiz.core.core.types import ErrDict


class ActionErrorsMan:
  def __init__(self):
    self.errdicts: List[ErrDict] = []

  def add_errors(self, errdicts: List[ErrDict]):
    for new_errdict in errdicts:
      new_err_id = new_errdict.get('uuid')
      if new_err_id:
        if not self.find_error(new_err_id):
          self.errdicts.append(new_errdict)
          print(f"added err {new_errdict}")
      else:
        print(f"[nectwiz::push_error] errdict missing uuid {new_errdict}")

  def find_error(self, error_id: str) -> Optional[ErrDict]:
    for errdict in self.errdicts:
      if errdict.get('uuid') == error_id:
        return errdict
    return None


errors_man = ActionErrorsMan()
