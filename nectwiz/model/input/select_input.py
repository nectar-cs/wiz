from typing import Optional, List, Dict

from nectwiz.model.input.input import GenericInput


class SelectInput(GenericInput):

  def implied_default(self) -> Optional[str]:
    options = self.options()
    return options[0].get('id') if len(options) > 0 else None

  def load_options(self) -> List[Dict]:
    if type(self.option_descs) == dict:
      trans = lambda item: {'id': item[0], 'title': item[1]}
      return list(map(trans, self.option_descs.items()))
    else:
      return self.option_descs
