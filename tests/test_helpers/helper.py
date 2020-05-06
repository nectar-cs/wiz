import json

import yaml

from k8_kat.auth.kube_broker import broker
from kubernetes.client import V1ConfigMap, V1ObjectMeta


def tedi_setup():
  return dict(
    te_type='kerbi',
    te_repo_name='https://github.com/nectar-cs/charts-and-wizards.git',
    te_repo_subpath='nectar-hub/kerbi-chart'
  )


def simple_tedi_setup():
  return dict(
    te_type='kerbi',
    te_repo_name='https://github.com/nectar-cs/charts-and-wizards.git',
    te_repo_subpath='wiz-ci/kerbi-chart'
  )


def create_base_master_map(ns):
  broker.coreV1.create_namespaced_config_map(
    namespace=ns,
    body=V1ConfigMap(
      metadata=V1ObjectMeta(
        namespace=ns,
        name='master'
      ),
      data=dict(master=yaml.dump({}))
    )
  )
