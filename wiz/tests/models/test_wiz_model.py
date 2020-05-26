import unittest
from typing import Type

from wiz.core.wiz_globals import wiz_app
from wiz.model.operations.operation import Operation
from wiz.model.field.field import Field
from wiz.model.step.step import Step
from wiz.model.base.wiz_model import WizModel
from wiz.tests.models.helpers import g_conf
from wiz.tests.t_helpers.cluster_test import ClusterTest

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
      self.assertEqual(inflated.key, 'a')
      self.assertEqual(inflated.title, 'a.title')

    def test_inflate_with_dict(self):
      config = g_conf(k='a', i=self.kind, t='foo', d='bar')
      inflated = self.model_class().inflate(config)
      self.assertEqual('foo', inflated.title)
      self.assertEqual('bar', inflated.info)

    def test_inflate_all(self):
      wiz_app.add_configs([
        g_conf(k='a', i=self.kind),
        g_conf(k='b', i=self.kind),
        g_conf(k='c', i=self.kind),
        g_conf(k='c', i=f"not-{self.kind}")
      ])

      actual = [c.key for c in self.model_class().inflate_all()]
      self.assertEqual(actual, ['a', 'b', 'c'])

    def test_inflate_when_subclassed(self):
      mks = self.model_class().type_key()
      class Sub(self.model_class()):
        @property
        def title(self):
          return "bar"

        @classmethod
        def key(cls):
          return "k"

        @classmethod
        def type_key(cls):
          return mks

      config = g_conf(k='k', i=self.kind, t='foo')
      wiz_app.add_overrides([Sub])
      inflated = self.model_class().inflate(config)
      self.assertEqual('bar', inflated.title)
