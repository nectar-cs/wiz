from typing import Dict, List, Optional, TypeVar

from werkzeug.utils import cached_property

from nectwiz.core.core.types import KoD
from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.error.error_context import ErrCtx
from nectwiz.model.error.error_diagnosis import ErrorDiagnosis
from nectwiz.model.error.error_trigger_selector import ErrorTriggerSelector

T = TypeVar('T', bound='ErrorHandler')

class ErrorHandler(WizModel):

  DIAGNOSES_KEY = 'diagnoses'
  TRIGGER_SELECTOR_KEY = 'selector'

  def __init__(self, config: Dict):
    super().__init__(config)
    self.selector_kod: KoD = config.get('selector')

  @cached_property
  def trigger_selector(self) -> Optional[ErrorTriggerSelector]:
    return self.inflate_child(
      ErrorTriggerSelector,
      prop=self.TRIGGER_SELECTOR_KEY,
      safely=True
    )

  @cached_property
  def diagnoses(self) -> List[ErrorDiagnosis]:
    return self.inflate_children(
      ErrorDiagnosis,
      prop=self.DIAGNOSES_KEY
    )

  def match_confidence_score(self, err_cont: ErrCtx):
    if self.trigger_selector:
      return self.trigger_selector.match_confidence_score(err_cont)
    else:
      return 0

  @staticmethod
  def is_err_diagnosable(errdict: Dict) -> bool:
    return ErrorHandler.find_handler(errdict) is not None

  @staticmethod
  def find_handler(errdict: Dict) -> Optional[T]:
    candidates: List[ErrorHandler] = ErrorHandler.inflate_all()
    errctx = ErrCtx(errdict)
    winner, winner_score = None, 0
    for candidate in candidates:
      score = candidate.match_confidence_score(errctx)
      if score > winner_score:
        winner = candidate
    return winner

  @staticmethod
  def compute_diagnoses_ids(handler_id: str) -> List[str]:
    error_handler: ErrorHandler = ErrorHandler.inflate(handler_id)
    diagnosis_ids = []
    for diagnosis in error_handler.diagnoses:
      if diagnosis.compute_is_suitable():
        diagnosis_ids.append(diagnosis.id())
    return diagnosis_ids
