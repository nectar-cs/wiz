import unittest

import dotenv
from k8kat.auth.kube_broker import broker
from k8kat.utils.testing import ns_factory

from nectwiz.core.core import utils
from nectwiz.core.core.wiz_app import wiz_app


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
    wiz_app._ns = None
    wiz_app.clear()

  def tearDown(self) -> None:
    super().setUp()
    wiz_app._ns = None
    wiz_app.clear()


test_ready_obj = dict(ready=False)


def is_ready():
  return test_ready_obj['ready']


def update_readiness(readiness):
  test_ready_obj['ready'] = readiness
