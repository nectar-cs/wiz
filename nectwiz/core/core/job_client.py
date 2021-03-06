import json
from typing import Optional, Any, List, Dict, Callable

from rq import Queue
from rq.exceptions import NoSuchJobError
from rq.job import Job

from nectwiz.core.core.types import ProgressItem, KoD, ErrDict
from nectwiz.worker import conn


queue = Queue(connection=conn)

def enqueue_action(key_or_dict: KoD, **kwargs) -> str:
  return enqueue_func(load_and_perform_action, key_or_dict, **kwargs)


def enqueue_func(func: Callable, *args, **kwargs) -> str:
  job = queue.enqueue(func, *args, **kwargs)
  return job.get_id()


def find_job(job_id: str) -> Optional[Job]:
  try:
    return Job.fetch(job_id, connection=conn)
  except NoSuchJobError:
    return None


def ternary_job_status(job_id: str) -> Optional[str]:
  job = find_job(job_id)
  if job:
    if job.is_failed:
      return 'negative'
    elif job.is_finished:
      return 'positive' if job.result else 'negative'
    elif job.is_started or job.is_queued:
      return 'running'
    else:
      print(f"[nectwiz::jobclient] Danger job status {job.get_status()}")
  return None


def job_meta(job_id: str) -> Dict:
  job: Job = find_job(job_id)
  return job.meta if job else {}


def job_meta_part(job_id: str, part_key: str) -> Dict:
  blob = job_meta(job_id).get(part_key)
  return json.loads(blob) if blob else {}


def job_progress(job_id: str) -> Optional[ProgressItem]:
  return job_meta_part(job_id, 'progress')


def job_result(job_id: str) -> Optional[Any]:
  return job_meta_part(job_id, 'result')


def job_telem(job_id: str) -> Optional[Any]:
  return job_meta_part(job_id, 'telem')


def job_errdicts(job_id: str) -> List[ErrDict]:
  blob = job_meta(job_id).get('errdicts')
  return json.loads(blob) if blob else {}


def load_and_perform_action(key_or_dict, **kwargs):
  from nectwiz.model.action.base.action import Action
  model: Action = Action.inflate(key_or_dict)
  print(model.config)
  print(f"OUR KWARGS {type(kwargs)}")
  print(kwargs)
  return model.run(**kwargs)
