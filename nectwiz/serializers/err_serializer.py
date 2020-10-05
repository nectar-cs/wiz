from nectwiz.model.error.error_diagnosis import ErrorDiagnosis


def ser_err_diagnosis(diagnosis: ErrorDiagnosis):
  actionables = diagnosis.actionables()
  return dict(
    title=diagnosis.title,
    info=diagnosis.info,
    actionables=actionables,
  )
