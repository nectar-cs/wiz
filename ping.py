from nectwiz.core.job import job_client

config = dict(
  kind='CmdExecAction',
  cmd='kubectl get ns -o json'
)

job_id = job_client.enqueue_action(config)
