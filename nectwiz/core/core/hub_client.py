import os

import requests
from k8kat.auth.kube_broker import broker

from nectwiz.core.core import utils
from nectwiz.core.core.config_man import config_man

api_path = '/cli'


def backend_host() -> str:
    if utils.is_dev():
      if broker.is_in_cluster_auth():
        return "http://necthub.com.ngrok.io"
      else:
        return 'http://localhost:3000'
    else:
      return 'https://api.codenectar.com'


def post(endpoint, payload):
  url = f'{backend_host()}{api_path}{endpoint}'
  print(f"[nectwiz:hub_client] post {url}")
  return requests.post(
    url,
    json=payload,
    headers={'Installuuid': config_man.install_uuid()}
  )


def patch(endpoint, payload):
  url = f'{backend_host()}{api_path}{endpoint}'
  print(f"[nectwiz:hub_client] patch {url}")
  return requests.patch(
    url,
    json=payload,
    headers={'Installuuid': config_man.install_uuid()}
  )


def get(endpoint):
  url = f'{backend_host()}{api_path}{endpoint}'
  print(f"[nectwiz:hub_client] get {url}")
  return requests.get(
    url,
    headers={'Installuuid': config_man.install_uuid()}
  )
