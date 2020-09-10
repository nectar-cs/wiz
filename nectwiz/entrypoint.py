import sys

from k8kat.auth.kube_broker import broker

from nectwiz import server, worker
from nectwiz.core.core import utils


def start():
  broker.connect()
  if utils.is_server():
    server.start()
  elif utils.is_worker():
    worker.start()
  else:
    print(f"Unrecognized exec mode {utils.exec_mode()}")
    sys.exit(1)
