import os

import redis
from rq import Worker, Queue, Connection

from nectwiz.core.core.config_man import config_man

redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')

conn = redis.from_url(redis_url)

def start():
  with Connection(conn):
    worker = Worker(list(map(Queue, ['default'])))
    worker.work()
