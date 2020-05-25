import unittest

from wiz.core.wiz_globals import wiz_globals as wg
from wiz.model.operations.operation import Operation
from wiz.tests.models.helpers import g_con_conf, g_conf


class TestOperation(unittest.TestCase):

  def setUp(self) -> None:
    wg.clear()

  def test_first_step_key(self):
    wg.set_configs(operations=[g_con_conf(k='k', s=['s2', 's1'])])
    actual = Operation.inflate('k').first_step_key()
    self.assertEqual(actual, 's2')

  def test_step(self):
    wg.set_configs(
      operations=[g_con_conf(k='c1', s=['s1', 's2'])],
      steps=[g_conf(k='s1', t='foo')]
    )

    c1 = Operation.inflate('c1')
    s1 = c1.step('s1')
    self.assertEqual(s1.key, 's1')
    self.assertEqual(s1.title, 'foo')


if __name__ == '__main__':
  unittest.main()
