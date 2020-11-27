from nectwiz.core.core import utils
from nectwiz.core.core.types import KAOs
from nectwiz.core.tam.tam_client import TamClient


def g_conf(**kwargs):
  key = kwargs.pop('k', 'key')

  return dict(
    id=key,
    kind=kwargs.pop('i', 'kind'),
    title=kwargs.pop('t', f'{key}.title'),
    info=kwargs.pop('d', f'{key}.desc'),
    **kwargs
  )

def tam_apply_cmap(ns: str) -> KAOs:
  return TamClient.kubectl_apply([
    dict(
      apiVersion='v1',
      kind='ConfigMap',
      metadata=dict(name='cm-good', namespace=ns),
      data={}
    )
  ])

def bad_cmap_kao(ns: str) -> KAOs:
  return TamClient.kubectl_apply([
    dict(
      apiVersion='v1',
      kind='ConfigMap',
      metadata=dict(name='cm-bad', namespace=ns),
      data='wrong-format'
    )
  ])

def tam_apply_pod(**kwargs) -> KAOs:
  return TamClient.kubectl_apply([
    dict(
      apiVersion='v1',
      kind='Pod',
      metadata=dict(
        name=kwargs.get('name', 'pod'),
        namespace=kwargs['ns']
      ),
      spec=dict(
        containers=[
          dict(
            name='main',
            image=kwargs.get('image', 'nginx')
          )
        ]
      )
    )
  ])
