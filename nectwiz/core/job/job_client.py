import json
from typing import Optional

from rq import Queue
from rq.job import Job

from nectwiz.core.core.types import ProgressItem
from nectwiz.worker import conn


queue = Queue(connection=conn)

def enqueue_action(key_or_dict, **kwargs):
  return enqueue_func(load_and_perform_action, key_or_dict, **kwargs)


def enqueue_func(func, *args, **kwargs):
  job = queue.enqueue(func, *args, **kwargs)
  return job.get_id()


def find_job(job_id: str) -> Job:
  return Job.fetch(job_id, connection=conn)


def ternary_job_status(job_id: str) -> Optional[str]:
  job = find_job(job_id)
  if job:
    if job.is_failed:
      return 'negative'
    elif job.is_finished:
      return 'positive'
    elif job.is_started or job.is_queued:
      return 'running'
    else:
      print(f"[nectwiz::jobclient] Danger job status {job.get_status()}")
  return None


def job_progress(job_id: str) -> Optional[ProgressItem]:
  job: Job = find_job(job_id)
  blob = job.meta.get('progress')
  return json.loads(blob) if blob else {}


def load_and_perform_action(key_or_dict, **kwargs):
  from nectwiz.model.action.action import Action
  print("COMING IN HOT")
  print(key_or_dict)
  print(kwargs)
  model: Action = Action.inflate(key_or_dict)
  return model.run(**kwargs)
