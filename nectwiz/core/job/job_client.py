from rq import Queue
from rq.job import Job

from nectwiz.worker import conn


def enqueue_action(key_or_dict, **kwargs):
  queue = Queue(connection=conn)
  job = queue.enqueue(load_and_perform_action, key_or_dict, **kwargs)
  return job.get_id()


def find_job(job_id: str) -> Job:
  return Job.fetch(job_id, connection=conn)

def load_and_perform_action(key_or_dict, **kwargs):
  from nectwiz.model.action.action import Action
  print("COMING IN HOT")
  print(key_or_dict)
  print(kwargs)
  model: Action = Action.inflate(key_or_dict)
  return model.perform(**kwargs)
