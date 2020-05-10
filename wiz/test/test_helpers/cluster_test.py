import unittest

import dotenv
from k8_kat.utils.testing import ci_perms, ns_factory

from wiz.core.wiz_globals import wiz_globals


class ClusterTest(unittest.TestCase):

  def setUp(self) -> None:
    super().setUp()
    wiz_globals.ns_overwrite = None

  @classmethod
  def setUpClass(cls) -> None:
    dotenv.load_dotenv()
    ci_perms.init_test_suite(False)

  @classmethod
  def tearDownClass(cls) -> None:
    ns_factory.relinquish_all()