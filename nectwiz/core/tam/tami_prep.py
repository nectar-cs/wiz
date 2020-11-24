from typing import List, Optional, Dict

import yaml
from k8kat.auth.kube_broker import broker
from k8kat.res.pod.kat_pod import KatPod
from kubernetes.client import V1Pod, V1ObjectMeta, \
  V1PodSpec, V1Container, \
  V1Volume, V1VolumeMount, V1ConfigMapVolumeSource, \
  V1ResourceRequirements, V1KeyToPath, V1ConfigMap

from nectwiz.core.core import utils
from nectwiz.core.core.config_man import tam_vars_key

values_mount_dir = '/values'
values_file_path = 'master'


def consume(**kwargs) -> Optional[str]:
  ns: str = kwargs.get('ns')
  image: str = kwargs.get('image')
  arglist: List[str] = kwargs.get('arglist')
  values: Optional[Dict] = kwargs.get('values')

  pod_name = f"tami-{utils.rand_str()}"

  if values is not None:
    broker.coreV1.create_namespaced_config_map(
      namespace=ns,
      body=V1ConfigMap(
        metadata=V1ObjectMeta(
          name=pod_name,
          namespace=ns,
          labels=dict(app=pod_name)
        ),
        data={
          values_file_path: yaml.dump(values)
        }
      )
    )

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
        volumes=volumes(pod_name, values),
        containers=[
          V1Container(
            name='main',
            image=image,
            args=arglist,
            # image_pull_policy='IfNotPresent' if utils.is_prod() else 'Always',
            image_pull_policy='Always',
            volume_mounts=volume_mounts(values),
            resources=V1ResourceRequirements(
              requests=dict(cpu='20m', memory='30M'),
              limits=dict(cpu='40m', memory='60M')
            )
          )
        ]
      )
    )
  )

  return KatPod.consume_runner(pod_name, ns, False)


def volumes(pod_name: str, values: Dict) -> List[V1Volume]:
  if values is not None:
    return [
      V1Volume(
        name='master',
        config_map=V1ConfigMapVolumeSource(
          name=pod_name,
          items=[V1KeyToPath(key=tam_vars_key, path='master')]
        )
      )
    ]
  else:
    return []


def volume_mounts(values: Dict) -> List[V1VolumeMount]:
  if values is not None:
    return [
      V1VolumeMount(
        name='master',
        mount_path=values_mount_dir
      ),
    ]
