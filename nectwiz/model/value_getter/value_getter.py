from typing import Any, Optional

from nectwiz.model.base.wiz_model import WizModel


class ValueGetter(WizModel):
  def produce(self) -> Optional[Any]:
    pass
