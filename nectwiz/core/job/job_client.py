from typing import Type

from rq.job import Job

from nectwiz.model.action.action import Action

from redis import Redis
from rq import Queue

from nectwiz.worker import conn


def enqueue_action(action_cls: Type[Action], *args, **kwargs):
  queue = Queue(connection=conn)
  runnable_func = getattr(action_cls, 'perform')
  queue.enqueue(runnable_func, *args, **kwargs)


def find_job(job_id: str) -> Job:
  return Job.fetch(job_id, connection=conn)
