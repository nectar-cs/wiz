from typing import List, Optional

from k8_kat.auth.kube_broker import broker
from k8_kat.res.pod.kat_pod import KatPod
from kubernetes.client import V1Pod, V1ObjectMeta, \
  V1PodSpec, V1Container, \
  V1Volume, V1VolumeMount, V1ConfigMapVolumeSource, V1ResourceRequirements, V1KeyToPath

from nectwiz.core import utils

vars_mount_dir = '/values'
vars_file_name = 'master'


def consume(ns, image: str, args: List[str]) -> Optional[str]:
  """
  Runs a terminating pod, returns the output, and destroys the pod upon termination.
  :param ns: desired namespace for Tami container.
  :param image: desired image for Tami container.
  :param args: desiered args for Tami container.
  :return: logs from the Tami container.
  """
  pod_name = f"tami-{utils.rand_str()}"
  from nectwiz.core import config_man
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
            name='master-config-map',
            config_map=V1ConfigMapVolumeSource(
              name='master',
              items=[
                V1KeyToPath(
                  key=config_man.tam_vars_key,
                  path=vars_file_name
                )
              ]
            )
          )
        ],
        containers=[
          V1Container(
            name='main',
            image=image,
            # command=["/bin/sh", "-c", "--" ],
            # args=["while true; do sleep 30; done;" ],
            args=args,
            image_pull_policy='Always' if utils.is_prod() else 'IfNotPresent',
            volume_mounts=volume_mounts(),
            resources=V1ResourceRequirements(
              requests=dict(cpu='20m', memory='100M'),
              limits=dict(cpu='40m', memory='200M')
            )
          )
        ]
      )
    )
  )

  return KatPod.consume_runner(pod_name, ns, False)


def volume_mounts() -> List[V1VolumeMount]:
  """
  Creates a volume mount.
  :return: volume mount data.
  """
  return [
    V1VolumeMount(
      name='master-config-map',
      mount_path=vars_mount_dir
    ),
  ]
