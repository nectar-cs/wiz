from typing import Optional, Dict

from nectwiz.model.base.wiz_model import WizModel


class StoreAdapter(WizModel):
  def __init__(self, config: Dict):
    super().__init__(config)
    self.friendly_db_name = config.get('friendly_db_name')

  def capacity_bytes(self) -> Optional[int]:
    raise NotImplemented

  def used_bytes(self) -> Optional[int]:
    raise NotImplemented
