from wiz.model.operations.operation import Operation


def standard(operation: Operation):
  return dict(
    id=operation.key,
    title=operation.title,
    description=operation.description,
    first_step_id=operation.first_step_key(),
    res_access=operation.res_access()
  )
