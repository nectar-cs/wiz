from kubernetes.client import V1ConfigMap, V1ObjectMeta, V1Job, V1JobSpec, V1PodTemplate

from k8_kat.auth.kube_broker import broker
from wiz.core.wiz_globals import wiz_app


def create_shared_config_map(job_name):
  return broker.coreV1.create_namespaced_config_map(
    namespace=wiz_app.ns,
    body=V1ConfigMap(
      metadata=V1ObjectMeta(
        name=f"{job_name}-storage-map"
      ),
      data=dict()
    )
  )


def create_job():
  return broker.coreV1.create_namespaced_job(
    namespace=wiz_app.ns,
    body=V1Job(
      metadata=V1ObjectMeta(

      ),
      spec=V1JobSpec(
        template=V1PodTemplate(

        )
      )
    )
  )

def prep_job():
  pass
