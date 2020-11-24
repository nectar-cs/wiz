import unittest

import dotenv
from k8kat.auth.kube_broker import broker
from k8kat.utils.testing import ns_factory

from nectwiz.core.core import utils
from nectwiz.core.core.config_man import config_man
from nectwiz.model.base.wiz_model import models_man


class ClusterTest(unittest.TestCase):

  @classmethod
  def setUpClass(cls) -> None:
    super().setUpClass()
    if not is_ready():
      dotenv.load_dotenv()
      utils.set_run_env('test')
      broker.connect()
      update_readiness(True)

  @classmethod
  def tearDownClass(cls) -> None:
    ns_factory.relinquish_all()

  def setUp(self) -> None:
    super().setUp()
    config_man._ns = None
    models_man.clear()
    ns_factory.update_max_ns(25)

  def tearDown(self) -> None:
    super().setUp()
    config_man._ns = None
    models_man.clear()


test_ready_obj = dict(ready=False)


def is_ready():
  return test_ready_obj['ready']


def update_readiness(readiness):
  test_ready_obj['ready'] = readiness
