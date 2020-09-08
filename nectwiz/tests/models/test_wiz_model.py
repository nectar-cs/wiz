from typing import Type

from nectwiz.core.core.wiz_app import wiz_app
from nectwiz.model.operations.operation import Operation
from nectwiz.model.field.field import Field
from nectwiz.model.step.step import Step
from nectwiz.model.base.wiz_model import WizModel
from nectwiz.tests.models.helpers import g_conf
from nectwiz.tests.t_helpers.cluster_test import ClusterTest

SUBCLASSES: [WizModel] = [Operation, Step, Field]


class Base:
  class TestWizModel(ClusterTest):

    def setUp(self) -> None:
      wiz_app.clear()

    @classmethod
    def model_class(cls) -> Type[WizModel]:
      raise NotImplementedError

    @property
    def kind(self):
      return self.model_class().type_key()

    def test_inflate_with_key(self):
      a, b = [g_conf(k='a', i=self.kind), g_conf(k='b', i=self.kind)]
      wiz_app.add_configs([a, b])
      inflated = self.model_class().inflate('a')
      self.assertEqual(type(inflated), self.model_class())
      self.assertEqual(inflated.id(), 'a')
      self.assertEqual(inflated.title, 'a.title')

    def test_inflate_with_dict(self):
      config = g_conf(i=self.kind, t='foo', d='bar')
      inflated = self.model_class().inflate(config)
      self.assertEqual('foo', inflated.title)
      self.assertEqual('bar', inflated.info)

    def test_inflate_all(self):
      wiz_app.configs = []
      wiz_app.add_configs([
        g_conf(k='a', i=self.kind),
        g_conf(k='b', i=self.kind),
        g_conf(k='c', i=self.kind),
        g_conf(k='c', i=f"not-{self.kind}")
      ])

      actual = [c.key for c in self.model_class().inflate_all()]
      self.assertEqual(actual, ['a', 'b', 'c'])

    def test_inflate_when_inherited(self):
      pass

    def test_inflate_when_subclassed(self):
      class Sub(self.model_class()):
        @property
        def title(self):
          return "bar"

        @classmethod
        def expected_key(cls):
          return 'k'

      config = g_conf(k='k', i=self.kind, t='foo')
      wiz_app.add_overrides([Sub])

      inflated = self.model_class().inflate(config)
      self.assertEqual('bar', inflated.title)
