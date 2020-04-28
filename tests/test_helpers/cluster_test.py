import unittest

import dotenv
from k8_kat.utils.testing import ci_perms, test_env


class ClusterTest(unittest.TestCase):

  @classmethod
  def setUpClass(cls) -> None:
    dotenv.load_dotenv()
    ci_perms.init_test_suite(False)
    test_env.cleanup()
    test_env.create_namespaces()
