import sys

from nectwiz import server, worker
from nectwiz.core.core import utils


def start():
  if utils.is_server():
    server.start()
  elif utils.is_server():
    exit_status = 0 if worker.start() else 1
    sys.exit(exit_status)
  else:
    print(f"Unrecognized exec mode {utils.exec_mode()}")
    sys.exit(1)
