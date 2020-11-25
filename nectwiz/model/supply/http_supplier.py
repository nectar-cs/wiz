from typing import Dict, Any, Optional, List

import requests

from nectwiz.model.supply.value_supplier import ValueSupplier


class HttpSupplier(ValueSupplier):

  def __init__(self, config: Dict):
    super().__init__(config)
    self.endpoint = config.get('endpoint')
    self.return_property = config.get('property', 'status_code')

  def _compute(self) -> Any:
    # noinspection PyBroadException
    try:
      response = requests.get(self.endpoint)
      if self.return_property in ['code', 'status', 'status_code']:
        return response.status_code
      elif self.return_property == 'json':
        return response.json()
      else:
        print("[nectwiz:http_getter]")
    except:
      return None
