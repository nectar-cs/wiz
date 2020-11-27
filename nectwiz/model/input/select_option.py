from typing import Dict

from nectwiz.model.base.wiz_model import WizModel


class SelectOption(WizModel):
  def serialize(self) -> Dict:
    return {
      'id': self.id(),
      'title': self.title
    }
