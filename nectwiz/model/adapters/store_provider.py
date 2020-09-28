from typing import List

from nectwiz.model.adapters.store_adapter import StoreAdapter
from nectwiz.model.base.wiz_model import WizModel


class StoresProvider(WizModel):

  # noinspection PyMethodMayBeStatic
  def store_adapters(self) -> List[StoreAdapter]:
    return StoreAdapter.inflate_all()
