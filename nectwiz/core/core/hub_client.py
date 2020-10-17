import os

import requests

from nectwiz.core.core import utils
from nectwiz.core.core.config_man import config_man

api_path = '/cli'

def backend_host() -> str:
  expl_value = os.environ.get('HUB_HOST')
  if expl_value:
    return expl_value
  else:
    print(f"[nectwiz::hub_client] danger $HUB_HOST not defined")
    if utils.is_dev():
      return 'http://localhost:3000'
    else:
      return 'https://api.codenectar.com'


def post(endpoint, payload):
  url = f'{backend_host()}{api_path}{endpoint}'
  return requests.post(
    url,
    json=payload,
    headers={'Installuuid': config_man.install_uuid()}
  )


def patch(endpoint, payload):
  url = f'{backend_host()}{api_path}{endpoint}'
  return requests.patch(
    url,
    json=payload,
    headers={'Installuuid': config_man.install_uuid()}
  )


def get(endpoint):
  url = f'{backend_host()}{api_path}{endpoint}'
  return requests.get(
    url,
    headers={'Installuuid': config_man.install_uuid()}
  )
