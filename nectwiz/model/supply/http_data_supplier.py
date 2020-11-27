from typing import Any

import requests
from werkzeug.utils import cached_property

from nectwiz.model.supply.value_supplier import ValueSupplier


class HttpDataSupplier(ValueSupplier):

  ENDPOINT_KEY = 'endpoint'

  @cached_property
  def endpoint(self):
    return self.resolve_prop(self.ENDPOINT_KEY, warn=True)

  @cached_property
  def output_format(self):
    super_value = super(HttpDataSupplier, self).output_format
    return super_value or 'status_code'

  # noinspection PyBroadException
  def _compute(self) -> Any:
    try:
      response = requests.get(self.endpoint)
      body_dict = {}
      try:
        body_dict = response.json()
      except:
        pass
      return dict(
        status_code=response.status_code,
        body=body_dict
      )
    except:
      return None
