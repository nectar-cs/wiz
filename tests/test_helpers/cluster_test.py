import unittest

import dotenv
from k8_kat.utils.testing import ci_perms, ns_factory


class ClusterTest(unittest.TestCase):

  @classmethod
  def setUpClass(cls) -> None:
    dotenv.load_dotenv()
    ci_perms.init_test_suite(False)

  @classmethod
  def tearDownClass(cls) -> None:
    ns_factory.relinquish_all()
