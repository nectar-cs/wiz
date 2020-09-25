from nectwiz.model.input.input import GenericInput


def in_variable(ginput: GenericInput):
  return dict(
    type=ginput.kind(),
    options=ginput.options(),
    extras=ginput.extras()
  )