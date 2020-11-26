from typing import List, Optional

from werkzeug.utils import cached_property

from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.error.diagnosis_actionable import DiagnosisActionable
from nectwiz.model.predicate.predicate import Predicate


class ErrorDiagnosis(WizModel):

  PREDICATE_KEY = 'predicate'
  ACTIONABLES_KEY = 'actionables'

  @cached_property
  def predicate(self) -> Optional[Predicate]:
    return self.inflate_child(
      Predicate,
      prop=self.PREDICATE_KEY
    )

  @cached_property
  def actionables(self) -> List[DiagnosisActionable]:
    return self.inflate_children(
      DiagnosisActionable,
      prop=self.ACTIONABLES_KEY
    )

  def compute_is_suitable(self) -> bool:
    if self.predicate:
      return self.predicate.evaluate()
    else:
      return True
