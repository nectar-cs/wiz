from nectwiz.core.core import consts
from nectwiz.core.core.config_man import config_man
from nectwiz.core.tam.local_exec_tam_client import LocalExecTamClient
from nectwiz.core.tam.tam_client import TamClient, TamClientConstructorArgs
from nectwiz.core.tam.http_api_tam_client import HttpApiTamClient


def tam_client(**kwargs: TamClientConstructorArgs) -> TamClient:
  tam = kwargs.pop('tam', None) or config_man.tam()
  tam_type = tam['type']

  if tam_type == consts.http_api_tam:
    return HttpApiTamClient(tam=tam, **kwargs)
  elif tam_type == consts.local_exec_tam:
    return LocalExecTamClient(tam=tam, **kwargs)
  elif tam_type == consts.virtual_tam:
    return tam['uri'](**kwargs)
  else:
    raise RuntimeError(f"Illegal TAM type {tam_type}")
