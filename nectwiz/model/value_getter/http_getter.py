from typing import Dict, Any, Optional

import requests

from nectwiz.model.value_getter.value_getter import ValueGetter


class HttpGetter(ValueGetter):

  def __init__(self, config: Dict):
    super().__init__(config)
    self.endpoint = config.get('endpoint')
    self.return_property = config.get('property', 'status_code')

  def produce(self) -> Optional[Any]:
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
