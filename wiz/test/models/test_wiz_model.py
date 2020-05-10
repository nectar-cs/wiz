import unittest
from wiz.core.wiz_globals import wiz_globals as wg
from wiz.model.concern.concern import Concern
from wiz.model.field.field import Field
from wiz.model.step.step import Step
from wiz.model.base.wiz_model import WizModel
from wiz.test.models.helpers import g_conf

SUBCLASSES: [WizModel] = [Concern, Step, Field]

class TestWizModel(unittest.TestCase):

  @property
  def crt_conf_category(self) -> str:
    return self.crt_subclass.type_key()

  def run_inflate_no_subclass(self):
    a, b = [g_conf(k='a'), g_conf(k='b')]
    wg.set_configs(**{self.crt_conf_category: [a, b]})
    inflated = self.crt_subclass.inflate('a')
    self.assertEqual(type(inflated), self.crt_subclass)
    self.assertEqual(inflated.key, 'a')
    self.assertEqual(inflated.title, 'a.title')

  def run_inflate_all(self):
    wg.set_configs(**{
      self.crt_conf_category: [
        g_conf(k='a'),
        g_conf(k='b'),
        g_conf(k='c'),
      ]
    })

    actual = [c.key for c in self.crt_subclass.inflate_all()]
    self.assertEqual(actual, ['a', 'b', 'c'])

  def run_inflate_with_subclass(self):
    class Sub(self.crt_subclass):
      def __init__(self, config):
        super().__init__(config)
        self.title = 'Override'

      @classmethod
      def key(cls):
        return "sub"

    wg.set_configs(**{
      self.crt_conf_category: [
        g_conf(k='sub'),
        g_conf(k='norm'),
      ]
    })

    wg.set_subclasses(**{self.crt_conf_category: [Sub]})
    sub, norm = self.crt_subclass.inflate('sub'), self.crt_subclass.inflate('norm')

    self.assertEqual(type(sub), Sub)
    self.assertEqual(sub.title, 'Override')

    self.assertNotEqual(type(norm), Sub)
    self.assertEqual(norm.title, 'norm.title')

  def test_inflate_no_subclass(self):
    for subclass in SUBCLASSES:
      self.crt_subclass = subclass
      self.run_inflate_no_subclass()

  def test_inflate_all(self):
    for subclass in SUBCLASSES:
      self.crt_subclass = subclass
      self.run_inflate_all()

  def test_inflate_with_subclass(self):
    for subclass in SUBCLASSES:
      self.crt_subclass = subclass
      self.run_inflate_with_subclass()
