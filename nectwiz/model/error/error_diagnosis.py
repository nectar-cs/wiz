from functools import lru_cache
from typing import Dict, List, Optional

from nectwiz.core.core.types import KoD
from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.error.diagnosis_actionable import DiagnosisActionable
from nectwiz.model.predicate.predicate import Predicate


class ErrorDiagnosis(WizModel):
  def __init__(self, config: Dict):
    super().__init__(config)
    self.predicate_kod: KoD = config.get('predicate')

  def compute_is_suitable(self) -> bool:
    if self.predicate():
      return self.predicate().evaluate({})
    else:
      return True

  @lru_cache(maxsize=1)
  def predicate(self) -> Optional[Predicate]:
    if self.predicate_kod:
      return Predicate.inflate(self.predicate_kod)

  def actionables(self) -> List[DiagnosisActionable]:
    return self.inflate_children('actionables', DiagnosisActionable)
