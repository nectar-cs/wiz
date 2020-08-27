from nectwiz.core.tam.tam_client import TamClient
from nectwiz.core.tam.tami_client import TamiClient
from nectwiz.core.tam.tams_client import TamsClient


def tam_client() -> TamClient:
  from nectwiz.core.wiz_app import wiz_app
  tam_type = wiz_app.tam()['type']
  overrider = wiz_app.tam_client_override

  if overrider:
    return overrider()
  elif tam_type == 'image':
    return TamiClient()
  elif tam_type == 'server':
    return TamsClient()
