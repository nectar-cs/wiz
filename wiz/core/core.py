import os

from kubernetes.client import V1ConfigMap, V1ObjectMeta

from k8_kat.auth.kube_broker import broker
from k8_kat.res.config_map.kat_map import KatMap

def namespace():
  return os.environ.get('NAMESPACE', 'moz')

def create_master_map():
  raw = broker.coreV1.create_namespaced_config_map(
    namespace=namespace(),
    body=V1ConfigMap(
      metadata=V1ObjectMeta(name='master'),
      data=dict(master='{}')
    )
  )

  return KatMap(raw)

def reset_master_map():
  master_map().delete() if master_map() else None
  return create_master_map()

def master_map():
  return KatMap.find(namespace(), 'master')

