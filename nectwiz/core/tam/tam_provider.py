from nectwiz.core.core.config_man import config_man
from nectwiz.core.core.types import TamDict
from nectwiz.core.tam.tamle_client import TamleClient
from nectwiz.core.tam.tam_client import TamClient
from nectwiz.core.tam.tami_client import TamiClient
from nectwiz.core.tam.tams_client import TamsClient


def tam_client(tam: TamDict = None) -> TamClient:
  tam = tam or config_man.tam()
  tam_type = tam['type']

  if tam_type == 'image':
    return TamiClient(tam)
  elif tam_type == 'server':
    return TamsClient(tam)
  elif tam_type == 'local_executable':
    return TamleClient(tam)
  else:
    raise RuntimeError(f"Illegal TAM type {tam_type}")
