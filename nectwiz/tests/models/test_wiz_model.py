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
      wiz_app.clear(restore_defaults=False)

    @classmethod
    def model_class(cls) -> Type[WizModel]:
      raise NotImplementedError

    @property
    def kind(self) -> str:
      return self.model_class().__name__

    def test_inflate_with_key(self):
      a, b = [g_conf(k='a', i=self.kind), g_conf(k='b', i=self.kind)]
      wiz_app.add_configs([a, b])
      inflated = self.model_class().inflate('a')
      self.assertEqual(type(inflated), self.model_class())
      self.assertEqual(inflated.id(), 'a')
      self.assertEqual(inflated.title, 'a.title')

    def test_inflate_with_config_simple(self):
      config = {'title': 'foo'}
      inflated = self.model_class().inflate_with_config(config)
      self.assertEqual('foo', inflated.title)
      self.assertEqual(self.model_class(), inflated.__class__)

    def test_inflate_with_config_inherit_easy(self):
      wiz_app.add_configs([{
        'kind': self.model_class().__name__,
        'id': 'parent',
        'title': 'yours'
      }])

      inheritor_config = {'id': 'mine', 'inherit': 'parent'}
      actual = self.model_class().inflate_with_config(inheritor_config)
      self.assertEqual(self.model_class(), actual.__class__)
      self.assertEqual('mine', actual.id())
      self.assertEqual('yours', actual.title)

    def test_inflate_with_config_inherit_hard(self):
      class SubModel(self.model_class()):
        @property
        def info(self):
          return 'grandpas'

      wiz_app.add_overrides([SubModel])
      wiz_app.add_configs([{
        'kind': SubModel.__name__,
        'id': 'parent',
        'title': 'yours',
        'info': 'yours'
      }])

      inheritor_config = {'id': 'mine', 'inherit': 'parent'}

      actual = self.model_class().inflate_with_config(inheritor_config)
      self.assertEqual(SubModel, actual.__class__)
      self.assertEqual('mine', actual.id())
      self.assertEqual('yours', actual.title)
      self.assertEqual('grandpas', actual.info)

    def test_inflate_with_config_expl_cls(self):
      class SubModel(self.model_class()):
        pass

      wiz_app.add_overrides([SubModel])
      inheritor_config = {'id': 'mine', 'kind': SubModel.__name__}
      actual = self.model_class().inflate_with_config(inheritor_config)
      self.assertEqual(SubModel, actual.__class__)

    def test_inflate_all(self):
      klass = self.model_class()

      class L1(klass):
        pass

      class L2(L1):
        pass

      wiz_app.add_configs([{
        'kind': klass.__name__,
        'id': 'lv0',
      }])

      wiz_app.add_configs([{
        'kind': f"not-{klass.__name__}",
        'id': 'should-not-appear',
      }])

      wiz_app.add_configs([{
        'kind': L2.__name__,
        'id': 'lv2',
      }])

      wiz_app.add_overrides([L1, L2])

      sig = lambda inst: {'id': inst.id(), 'cls': inst.__class__}
      from_lv0 = list(map(sig, klass.inflate_all()))
      exp = [{'id': 'lv0', 'cls': klass}, {'id': 'lv2', 'cls': L2}]
      self.assertEqual(exp, from_lv0)

    def test_load_children(self):

      class ChildClass(WizModel):
        pass

      wiz_app.add_configs([
        {
          'id': 'independent-child',
          'kind': ChildClass.__name__
        },
        {
          'id': 'non-child',
          'kind': ChildClass.__name__
        },
        {
          'id': 'parent',
          'kind': self.model_class().__name__,
          'children': [
            'independent-child',
            {'kind': ChildClass.__name__, 'id': 'embedded-child'}
          ]
        }
      ])

      wiz_app.add_overrides([ChildClass])
      parent_inst = self.model_class().inflate('parent')
      sig = lambda inst: {'id': inst.id(), 'cls': inst.__class__}
      result = parent_inst.load_children('children', ChildClass)
      exp = [
        {'id': 'independent-child', 'cls': ChildClass},
        {'id': 'embedded-child', 'cls': ChildClass}
      ]
      self.assertEqual(exp, list(map(sig, result)))
