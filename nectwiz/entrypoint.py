import sys

from k8kat.auth.kube_broker import broker

from nectwiz import server, worker
from nectwiz.core.core import utils
from nectwiz.model.base.wiz_model import models_man


def start():
  broker.connect()
  models_man.add_defaults()
  if utils.is_server():
    server.start()
  elif utils.is_worker():
    worker.start()
  elif utils.is_shell():
    from nectwiz import shell
    shell.start()
  else:
    print(f"Unrecognized exec mode {utils.exec_mode()}")
