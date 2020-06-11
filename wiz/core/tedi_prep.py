import time
from typing import List, Optional

from k8_kat.res.pod.kat_pod import KatPod
from kubernetes.client import V1Pod, V1ObjectMeta, \
  V1PodSpec, V1Container, \
  V1Volume, V1VolumeMount, V1ConfigMapVolumeSource

from k8_kat.auth.kube_broker import broker
from wiz.core import utils, wiz_globals


def consume(ns, image: str, args: List[str]) -> Optional[str]:

  pod_name = f"tedi-{utils.rand_str()}"

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
              name='master'
            )
          )
        ],
        containers=[
          V1Container(
            name='main',
            image=image,
            args=args,
            image_pull_policy='Always' if utils.is_prod() else 'IfNotPresent',
            volume_mounts=volume_mounts()
          )
        ]
      )
    )
  )

  return KatPod.consume_runner(pod_name, ns, False)



def volume_mounts() -> List[V1VolumeMount]:
  return [
    V1VolumeMount(
      name='master-config-map',
      mount_path='/values'
    ),
  ]
