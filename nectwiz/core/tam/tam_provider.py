from nectwiz.core.core.config_man import config_man
from nectwiz.core.tam.tamle_client import TamleClient
from nectwiz.core.tam.tam_client import TamClient
from nectwiz.core.tam.tami_client import TamiClient
from nectwiz.core.tam.tams_client import TamsClient


def tam_client() -> TamClient:
  
  print("AT THIS POINT THE NS IS")
  print(config_man.ns())
  print(config_man.tam())
  
  tam_type = config_man.tam()['type']

  if tam_type == 'image':
    return TamiClient()
  elif tam_type == 'server':
    return TamsClient()
  elif tam_type == 'local_executable':
    return TamleClient()
  else:
    raise RuntimeError(f"Illegal TAM type {tam_type}")
