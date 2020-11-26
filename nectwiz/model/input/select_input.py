from typing import Optional

from nectwiz.model.input.input import GenericInput


class SelectInput(GenericInput):

  # todo apparently not used; how could this be?
  def implied_default(self) -> Optional[str]:
    options = self.serialize_options()
    return options[0].get('id') if len(options) > 0 else None
