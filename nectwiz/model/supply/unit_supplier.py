from typing import Any

from werkzeug.utils import cached_property

from nectwiz.model.supply.value_supplier import ValueSupplier


class UnitSupplier(ValueSupplier):

  DATA_KEY = 'data'

  @cached_property
  def data(self):
    return self.resolve_prop(self.DATA_KEY, warn=True)

  def _compute(self) -> Any:
    return self.data
