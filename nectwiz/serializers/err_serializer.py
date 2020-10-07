from typing import Dict

from nectwiz.model.error.diagnosis_actionable import DiagnosisActionable
from nectwiz.model.error.error_diagnosis import ErrorDiagnosis


def ser_err_diagnosis(diagnosis: ErrorDiagnosis) -> Dict:
  actionables = list(map(ser_embedded_actionable, diagnosis.actionables()))

  return dict(
    id=diagnosis.id(),
    title=diagnosis.title,
    info=diagnosis.info,
    actionables=actionables,
  )


def ser_embedded_actionable(actionable: DiagnosisActionable) -> Dict:
  return dict(
    id=actionable.id(),
    title=actionable.title,
    info=actionable.info,
    operation_id=actionable.operation_id,

  )
