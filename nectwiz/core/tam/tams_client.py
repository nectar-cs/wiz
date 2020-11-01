from typing import Dict, List

import requests

from nectwiz.core.core.config_man import config_man
from nectwiz.core.tam.tam_client import TamClient
from nectwiz.core.core.types import K8sResDict


class TamsClient(TamClient):

  def load_manifest_defaults(self) -> Dict[str, str]:
    return http_get('/values')

  def load_templated_manifest(self, inlines=None) -> List[K8sResDict]:
    payload = dict(values=config_man.manifest_vars(force_reload=True))
    return http_post('/template', payload)


def base_url():
  return f"{config_man.tam()['uri']}/{config_man.tam()['version']}"


def http_post(endpoint, payload):
  url = f'{base_url()}{endpoint}'
  return requests.post(url, json=payload).json()


def http_get(endpoint):
  url = f'{base_url()}{endpoint}'
  return requests.get(url).json()
