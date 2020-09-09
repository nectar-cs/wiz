import os

import redis
from rq import Worker, Queue, Connection


redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')

conn = redis.from_url(redis_url)

def start():
  with Connection(conn):
    worker = Worker(list(map(Queue, ['default'])))
    worker.work()


if __name__ == '__main__':
  start()
