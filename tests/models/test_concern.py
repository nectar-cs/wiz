import unittest

from tests.models.helpers import g_con_conf
from wiz.core.wiz_globals import wiz_globals as wg
from wiz.model.concern.concern import Concern


class TestClusterConcern(unittest.TestCase):

  def setUp(self) -> None:
    wg.clear()

  def test_inflate_all(self):
    wg.set_configs(concerns=[
      g_con_conf(k='a'),
      g_con_conf(k='b'),
      g_con_conf(k='c'),
    ])

    actual = [c.key for c in Concern.inflate_all()]
    self.assertEqual(actual, ['a', 'b', 'c'])

  def test_inflate_no_subclass(self):
    a, b = [g_con_conf(k='a'), g_con_conf(k='b')]
    wg.set_configs(concerns=[a, b])
    inflated = Concern.inflate('a')
    self.assertEqual(type(inflated), Concern)
    self.assertEqual(inflated.key, 'a')
    self.assertEqual(inflated.title, 'a.title')

  def test_inflate_with_subclass(self):
    class Sub(Concern):
      def __init__(self, config):
        super().__init__(config)
        self.description = 'Override'

      @classmethod
      def key(cls):
        return "sub"

    wg.set_configs(concerns=[
      g_con_conf(k='sub'),
      g_con_conf(k='norm'),
    ])

    wg.set_subclasses(concerns=[Sub])
    sub, norm = Concern.inflate('sub'), Concern.inflate('norm')

    self.assertEqual(type(sub), Sub)
    self.assertEqual(sub.description, 'Override')

    self.assertNotEqual(type(norm), Sub)
    self.assertEqual(sub.description, 'Override')


if __name__ == '__main__':
  unittest.main()
