from typing import Type

from nectwiz.model.base.wiz_model import WizModel, models_man
from nectwiz.model.field.field import Field
from nectwiz.model.operation.operation import Operation
from nectwiz.model.operation.step import Step
from nectwiz.tests.models.helpers import g_conf
from nectwiz.tests.t_helpers.cluster_test import ClusterTest

SUBCLASSES: [WizModel] = [Operation, Step, Field]


class Base:
  class TestWizModel(ClusterTest):

    def setUp(self) -> None:
      models_man.clear(restore_defaults=False)

    @classmethod
    def model_class(cls) -> Type[WizModel]:
      raise NotImplementedError

    @property
    def kind(self) -> str:
      return self.model_class().__name__

    def test_inflate_with_id_key(self):
      a, b = [g_conf(k='a', i=self.kind), g_conf(k='b', i=self.kind)]
      models_man.add_descriptors([a, b])
      inflated = self.model_class().inflate('a')
      self.assertEqual(type(inflated), self.model_class())
      self.assertEqual(inflated.id(), 'a')
      self.assertEqual(inflated.title, 'a.title')

    def test_inflate_with_type_key(self):
      class Custom(self.model_class()):
        def __init__(self, config):
          super().__init__(config)
          self.info = 'baz'

      models_man.add_classes([Custom])
      result = self.model_class().inflate_with_key(Custom.__name__)
      self.assertEqual(Custom, result.__class__)
      self.assertEqual('baz', result.info)

    def test_inflate_with_config_simple(self):
      config = {'title': 'foo'}
      inflated = self.model_class().inflate_with_config(config)
      self.assertEqual('foo', inflated.title)
      self.assertEqual(self.model_class(), inflated.__class__)

    def test_inflate_with_config_inherit_easy(self):
      models_man.add_descriptors([{
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
        def __init__(self, config):
          super().__init__(config)
          self.info = 'grandpas'

      models_man.add_classes([SubModel])
      models_man.add_descriptors([{
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

      models_man.add_classes([SubModel])
      inheritor_config = {'id': 'mine', 'kind': SubModel.__name__}
      actual = self.model_class().inflate_with_config(inheritor_config)
      self.assertEqual(SubModel, actual.__class__)

    def test_inflate_all(self):
      klass = self.model_class()

      class L1(klass):
        pass

      class L2(L1):
        pass

      models_man.add_descriptors([{
        'kind': klass.__name__,
        'id': 'lv0',
      }])

      models_man.add_descriptors([{
        'kind': f"not-{klass.__name__}",
        'id': 'should-not-appear',
      }])

      models_man.add_descriptors([{
        'kind': L2.__name__,
        'id': 'lv2',
      }])

      models_man.add_classes([L1, L2])

      sig = lambda inst: {'id': inst.id(), 'cls': inst.__class__}
      from_lv0 = list(map(sig, klass.inflate_all()))
      exp = [{'id': 'lv0', 'cls': klass}, {'id': 'lv2', 'cls': L2}]
      self.assertEqual(exp, from_lv0)

    def test_load_children(self):

      class ChildClass(WizModel):
        pass

      models_man.add_descriptors([
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

      models_man.add_classes([ChildClass])
      parent_inst = self.model_class().inflate('parent')
      sig = lambda inst: {'id': inst.id(), 'cls': inst.__class__}
      result = parent_inst.inflate_children('children', ChildClass)
      exp = [
        {'id': 'independent-child', 'cls': ChildClass},
        {'id': 'embedded-child', 'cls': ChildClass}
      ]
      self.assertEqual(exp, list(map(sig, result)))
