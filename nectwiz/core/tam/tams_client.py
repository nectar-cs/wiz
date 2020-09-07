from typing import Dict, List

import requests

from nectwiz.core.core import config_man
from nectwiz.core.tam.tam_client import TamClient
from nectwiz.core.core.types import K8sResDict
from nectwiz.core.core.wiz_app import wiz_app


class TamsClient(TamClient):

  def load_manifest_defaults(self) -> Dict[str, str]:
    return http_get('/values')

  def load_tpd_manifest(self, inlines=None) -> List[K8sResDict]:
    payload = dict(values=config_man.read_tam_vars())
    return http_post('/template', payload)


def base_url():
  return f"{wiz_app.tam()['uri']}/{wiz_app.tam()['ver']}"


def http_post(endpoint, payload):
  url = f'{base_url()}{endpoint}'
  return requests.post(url, json=payload).json()


def http_get(endpoint):
  url = f'{base_url()}{endpoint}'
  return requests.get(url).json()
