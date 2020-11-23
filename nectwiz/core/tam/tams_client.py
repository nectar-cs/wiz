from typing import Dict, List

import requests

from nectwiz.core.core.config_man import config_man
from nectwiz.core.tam.tam_client import TamClient
from nectwiz.core.core.types import K8sResDict


class TamsClient(TamClient):

  def load_manifest_defaults(self) -> Dict[str, str]:
    return http_get('/values')

  def load_templated_manifest(self, inlines=None) -> List[K8sResDict]:
    endpoint = f"/template?release_name={config_man.ns()}"
    return http_post(endpoint, self.compute_values())


def base_url():
  tam = config_man.tam()
  version = f"/{tam['version']}" if tam['version'] else ''
  return f"{tam['uri']}#{version}"


def http_post(endpoint, payload):
  url = f'{base_url()}{endpoint}'
  response = requests.post(url, json=payload)
  return response.json().get('data')


def http_get(endpoint):
  url = f'{base_url()}{endpoint}'
  response = requests.get(url)
  return response.json().get('data')
