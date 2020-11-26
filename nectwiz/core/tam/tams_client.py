from typing import Dict, List
from urllib.parse import quote_plus

import requests

from nectwiz.core.core.config_man import config_man
from nectwiz.core.core.utils import flat2deep
from nectwiz.core.tam.tam_client import TamClient
from nectwiz.core.core.types import K8sResDict


class TamsClient(TamClient):

  def load_manifest_defaults(self) -> Dict[str, str]:
    return self.http_get(f"/values?{self.any_cmd_args()}")

  def load_templated_manifest(self, inlines: Dict) -> List[K8sResDict]:
    endpoint = f"/template?{self.template_cmd_args()}"
    payload = self.compute_values(flat2deep(inlines or {}))
    return self.http_post(endpoint, payload)

  def base_url(self):
    tam = self.tam
    version = tam.get('version')
    version_part = f"/{version}" if version else ''
    return f"{tam['uri']}{version_part}"

  def http_post(self, endpoint, payload):
    url = f'{self.base_url()}{endpoint}'
    print("FINAL URL")
    print(url)
    print(payload)
    response = requests.post(url, json=payload)
    return response.json().get('data')

  def http_get(self, endpoint):
    url = f'{self.base_url()}{endpoint}'
    response = requests.get(url)
    return response.json().get('data')

  def any_cmd_args(self) -> str:
    args_str = super().any_cmd_args()
    if args_str:
      return f"args={quote_plus(args_str)}"
    return ''

  def template_cmd_args(self, *args) -> str:
    std_part = self.any_cmd_args()
    if not config_man.ns():
      print("[nectwiz:tams+client] fatal ns is blank")
    ns_part = f"release_name={config_man.ns()}"
    std_part = f"&{std_part}" if std_part else ""
    return f"{ns_part}{std_part}"
