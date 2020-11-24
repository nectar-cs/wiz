from nectwiz.core.core.config_man import config_man
from nectwiz.core.core.types import TamDict
from nectwiz.core.tam.tamle_client import TamleClient
from nectwiz.core.tam.tam_client import TamClient
from nectwiz.core.tam.tami_client import TamiClient
from nectwiz.core.tam.tams_client import TamsClient


def tam_client(**kwargs) -> TamClient:
  tam = kwargs.pop('tam', None) or config_man.tam()
  tam_type = tam['type']

  if tam_type == 'image':
    return TamiClient(tam=tam, **kwargs)
  elif tam_type == 'server':
    return TamsClient(tam=tam, **kwargs)
  elif tam_type == 'local_executable':
    return TamleClient(tam=tam, **kwargs)
  else:
    raise RuntimeError(f"Illegal TAM type {tam_type}")
