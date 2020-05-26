from wiz.model.operations.operation import Operation


def standard(operation: Operation):
  return dict(
    id=operation.key,
    title=operation.title,
    description=operation.info,
    res_access=operation.res_access()
  )
