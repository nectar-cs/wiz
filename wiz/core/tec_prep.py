from kubernetes.client import V1Pod, V1ObjectMeta, \
  V1PodSpec, V1Container,\
  V1EnvVar, V1Volume, V1VolumeMount

from k8_kat.auth.kube_broker import broker

pod_name = 'ted'

def create(ns, app):
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
          )
        ],
        init_containers=[
          V1Container(
            name='init',
            image='gcr.io/nectar-bazaar/teds:latest',
            args=[app['te_type'], 'init'],
            image_pull_policy='Always',
            volume_mounts=[volume_mount()],
            env=env_vars(app)
          ),
        ],
        containers=[
          V1Container(
            name='main',
            image='gcr.io/nectar-bazaar/teds:latest',
            command=["/bin/sh", "-c", "--"],
            args=["while true; do sleep 10; done;"],
            image_pull_policy='Always',
            volume_mounts=[volume_mount()],
            env=env_vars(app)
          )
        ]
      )
    )
  )


def volume_mount():
  return V1VolumeMount(
    name='shared',
    mount_path='/tmp/work'
  )


def env_vars(app):
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
  ]
