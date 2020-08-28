import requests

from nectwiz.core import utils

api_path = '/api/cli'

def backend_host():
  if utils.is_dev():
    return 'http://localhost:3000'
  else:
    return 'https://api.codenectar.com'


def post(endpoint, payload):
  url = f'{backend_host()}{api_path}{endpoint}'
  return requests.post(url, json=payload)


def patch(endpoint, payload):
  url = f'{backend_host()}{api_path}{endpoint}'
  return requests.patch(url, json=payload)


def get(endpoint):
  url = f'{backend_host()}{api_path}{endpoint}'
  return requests.get(url)
