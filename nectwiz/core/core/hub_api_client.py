from typing import Optional

import requests

from nectwiz.core.core import utils
from nectwiz.core.core.config_man import config_man

api_path = '/cli'


def backend_host() -> Optional[str]:
  if config_man.is_training_mode():
    print("[nectwiz:hub_client] illegal call while training mode")
    return None
  if utils.is_dev():
    return "http://necthub.com.ngrok.io"
  else:
    return 'https://api.codenectar.com'


def post(endpoint, payload) -> requests.Response:
  url = f'{backend_host()}{api_path}{endpoint}'
  print(f"[nectwiz:hub_client] post {url}")
  return requests.post(
    url,
    json=payload,
    headers={'Installuuid': config_man.install_uuid()}
  )


def patch(endpoint, payload) -> requests.Response:
  url = f'{backend_host()}{api_path}{endpoint}'
  print(f"[nectwiz:hub_client] patch {url}")
  return requests.patch(
    url,
    json=payload,
    headers={'Installuuid': config_man.install_uuid()}
  )


def get(endpoint) -> requests.Response:
  url = f'{backend_host()}{api_path}{endpoint}'
  print(f"[nectwiz:hub_client] get {url}")
  return requests.get(
    url,
    headers={'Installuuid': config_man.install_uuid()}
  )
