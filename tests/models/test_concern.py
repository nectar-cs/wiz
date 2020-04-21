import unittest

from tests.models.helpers import g_con_conf
from wiz.core.wiz_globals import wiz_globals as wg
from wiz.model.concern.concern import Concern


class TestClusterConcern(unittest.TestCase):

  def test_inflate(self):
    a, b = [g_con_conf(k='a'), g_con_conf(k='b')]
    wg.set_configs(concerns=[a, b])
    inflated = Concern.inflate('a')
    self.assertEqual(type(inflated), Concern)
    self.assertEqual(inflated.key, 'a')
    self.assertEqual(inflated.title, 'a.title')

if __name__ == '__main__':
  unittest.main()
