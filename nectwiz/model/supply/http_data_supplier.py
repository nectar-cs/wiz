from typing import Dict, Any

import requests

from nectwiz.model.supply.value_supplier import ValueSupplier


class HttpDataSupplier(ValueSupplier):

  def __init__(self, config: Dict):
    super().__init__(config)
    self.endpoint = config.get('endpoint')
    self.desired_output_format = self.get_prop('output', 'status_code')

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
