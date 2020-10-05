from functools import lru_cache
from typing import Dict, List, Optional

from nectwiz.core.core.types import KoD, ErrDict
from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.error.error_context import ErrCtx
from nectwiz.model.error.error_diagnosis import ErrorDiagnosis
from nectwiz.model.error.error_trigger_selector import ErrorTriggerSelector


class ErrorHandler(WizModel):
  def __init__(self, config: Dict):
    super().__init__(config)
    self.selector_kod: KoD = config.get('selector')

  def match_confidence_score(self, err_cont: ErrCtx):
    if self.selector():
      return self.selector().match_confidence_score(err_cont)
    else:
      return 0

  @lru_cache(maxsize=1)
  def selector(self) -> Optional[ErrorTriggerSelector]:
    if self.selector_kod:
      return ErrorTriggerSelector.inflate(self.selector_kod)
    else:
      return None

  @lru_cache(maxsize=1)
  def diagnoses(self) -> List[ErrorDiagnosis]:
    return self.load_children('diagnoses', ErrorDiagnosis)


def find_handler(errdict: Dict) -> Optional[ErrorHandler]:
  candidates: List[ErrorHandler] = ErrorHandler.inflate_all()
  errctx = ErrCtx(errdict)
  winner, winner_score = None, 0
  for candidate in candidates:
    score = candidate.match_confidence_score(errctx)
    if score > winner_score:
      winner = candidate
  return winner


def compute_diagnoses_ids(handler_id: str) -> str:
  error_handler: ErrorHandler = ErrorHandler.inflate(handler_id)
  diagnosis_ids = []
  for diagnosis in error_handler.diagnoses():
    if diagnosis.compute_is_suitable():
      diagnosis_ids.append(diagnosis.id())
  return ",".join(diagnosis_ids)
