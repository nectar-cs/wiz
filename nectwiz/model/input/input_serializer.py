from nectwiz.model.input.generic_input import GenericInput


def in_variable(ginput: GenericInput):
  return dict(
    type=ginput.kind(),
    options=ginput.serialize_options(),
    extras=ginput.extras()
  )
