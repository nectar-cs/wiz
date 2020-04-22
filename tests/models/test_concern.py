import unittest

from tests.models.helpers import g_con_conf, g_conf
from wiz.core.wiz_globals import wiz_globals as wg
from wiz.model.concern.concern import Concern


class TestConcern(unittest.TestCase):

  def setUp(self) -> None:
    wg.clear()

  def test_first_step_key(self):
    wg.set_configs(concerns=[g_con_conf(s=['s2', 's1'])])
    actual = Concern.inflate('k').first_step_key()
    self.assertEqual(actual, 's2')

  def test_step(self):
    wg.set_configs(
      concerns=[g_con_conf(k='c1', s=['s1', 's2'])],
      steps=[g_conf(k='s1', t='foo')]
    )
    c1 = Concern.inflate('c1')
    s1 = c1.step('s1')
    self.assertEqual(s1.key, 's1')
    self.assertEqual(s1.title, 'foo')

if __name__ == '__main__':
  unittest.main()
