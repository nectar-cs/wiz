from typing import Optional

from nectwiz.model.input.input import GenericInput


class SelectInput(GenericInput):

  def implied_default(self) -> Optional[str]:
    options = self.serialize_options()
    return options[0].get('id') if len(options) > 0 else None
