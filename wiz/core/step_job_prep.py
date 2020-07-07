import json
from typing import Dict

from kubernetes.client import V1ConfigMap, V1ObjectMeta, V1Job, V1JobSpec, V1PodSpec, V1PodTemplateSpec, \
  V1Container, V1VolumeMount, V1Volume, V1ConfigMapVolumeSource, V1ResourceRequirements

from k8_kat.auth.kube_broker import broker
from wiz.core import utils
from wiz.core.wiz_globals import wiz_app


master_label = 'nectar-wiz-step'
dir_mount_path = '/etc/wiz-step'
status_fname = '/tmp/wiz-job-status.json'
params_fname = 'params.json'


def _create_shared_config_map(job_id, values: Dict):
  return broker.coreV1.create_namespaced_config_map(
    namespace=wiz_app.ns,
    body=V1ConfigMap(
      metadata=V1ObjectMeta(
        name=job_id,
        labels=dict(type=master_label)
      ),
      data={
        params_fname: json.dumps(values),
      }
    )
  )


def _create_job(job_id, image, command, args):
  return broker.batchV1.create_namespaced_job(
    namespace=wiz_app.ns,
    body=V1Job(
      metadata=V1ObjectMeta(
        name=job_id,
        labels=dict(type=master_label)
      ),
      spec=V1JobSpec(
        backoff_limit=0,
        ttl_seconds_after_finished=15,
        template=V1PodTemplateSpec(
          spec=V1PodSpec(
            restart_policy='Never',
            volumes=[
              V1Volume(
                name='params',
                config_map=V1ConfigMapVolumeSource(
                  name=job_id
                )
              ),
            ],
            containers=[
              V1Container(
                name='main',
                image=image,
                command=command,
                args=args,
                volume_mounts=[
                  V1VolumeMount(name='params',mount_path=dir_mount_path)
                ],
                resources=V1ResourceRequirements(
                  requests=dict(cpu='0.1', memory='100M'),
                  limits=dict(cpu='0.2', memory='150M')
                )
              )
            ]
          )
        )
      )
    )
  )


def create_and_run(image, command, args, values) -> str:
  job_id = utils.rand_str(string_len=10)
  _create_shared_config_map(job_id, values)
  _create_job(job_id, image, command, args)
  return job_id
