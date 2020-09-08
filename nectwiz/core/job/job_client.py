from typing import Type

from rq.job import Job

from nectwiz.model.action import action
from nectwiz.model.action.action import Action

from redis import Redis
from rq import Queue

from nectwiz.worker import conn


def enqueue_action(key_or_dict, **kwargs):
  queue = Queue(connection=conn)
  queue.enqueue(action.load_and_perform, *key_or_dict, **kwargs)


def find_job(job_id: str) -> Job:
  return Job.fetch(job_id, connection=conn)
