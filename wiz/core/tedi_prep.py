import time
from typing import List

from k8_kat.res.pod.kat_pod import KatPod
from kubernetes.client import V1Pod, V1ObjectMeta, \
  V1PodSpec, V1Container, \
  V1EnvVar, V1Volume, V1VolumeMount, V1ConfigMapVolumeSource

from k8_kat.auth.kube_broker import broker
from wiz.core import utils, wiz_globals

pod_name = wiz_globals.tedi_pod_name

def create(ns, app) -> None:
  broker.coreV1.create_namespaced_pod(
    namespace=ns,
    body=V1Pod(
      metadata=V1ObjectMeta(
        name=pod_name,
        namespace=ns,
        labels=dict(app=pod_name)
      ),
      spec=V1PodSpec(
        restart_policy='Never',
        volumes=[
          V1Volume(
            name='shared',
            empty_dir={}
          ),
          V1Volume(
            name='master-config-map',
            config_map=V1ConfigMapVolumeSource(
              name='master'
            )
          )
        ],
        init_containers=[
          V1Container(
            name='init',
            image='gcr.io/nectar-bazaar/teds:latest',
            args=[app['te_type'], 'init'],
            image_pull_policy='Always' if utils.is_prod() else 'IfNotPresent',
            volume_mounts=volume_mounts(),
            env=env_vars(app)
          ),
        ],
        containers=[
          V1Container(
            name='main',
            image='gcr.io/nectar-bazaar/teds:latest',
            command=["/bin/sh", "-c", "--"],
            args=["while true; do sleep 10; done;"],
            image_pull_policy='Always' if utils.is_prod() else 'IfNotPresent',
            volume_mounts=volume_mounts(),
            env=env_vars(app)
          )
        ]
      )
    )
  )

  while not KatPod.find(pod_name, ns):
    time.sleep(0.2)


def volume_mounts() -> List[V1VolumeMount]:
  return [
    V1VolumeMount(
      name='shared',
      mount_path='/tmp/work'
    ),
    V1VolumeMount(
      name='master-config-map',
      mount_path='/values'
    ),
  ]


def env_vars(app) -> List[V1EnvVar]:
  return [
    V1EnvVar(
      name='REPO_NAME',
      value=app['te_repo_name']
    ),
    V1EnvVar(
      name='CLONE_INTO_DIR',
      value='/tmp/clone-into'
    ),
    V1EnvVar(
      name='REPO_SUBPATH',
      value=app['te_repo_subpath']
    ),
    V1EnvVar(
      name='WORKING_DIR',
      value='/tmp/work'
    ),
    V1EnvVar(
      name='OVERRIDES_PATH',
      value='/values/master'
    )
  ]
