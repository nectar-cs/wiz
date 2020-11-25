from typing import Type, Any

from nectwiz.core.core.config_man import config_man
from nectwiz.model.base.wiz_model import WizModel, models_man
from nectwiz.model.field.field import Field
from nectwiz.model.operation.operation import Operation
from nectwiz.model.operation.step import Step
from nectwiz.model.predicate.common_predicates \
  import TruePredicate, FalsePredicate
from nectwiz.model.predicate.iftt import Iftt
from nectwiz.model.supply.value_supplier import ValueSupplier
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

    def test_try_as_iftt_when_not_iftt(self):
      config = dict(kind=self.model_class().kind(), id='foo')
      result = self.model_class().try_iftt_intercept(config, {})
      self.assertEqual(config, result)

    def test_get_prop_default(self):
      inst = self.model_class()(dict(foo='bar'))
      result = inst.resolve_prop('foo', 'backup', None)
      self.assertEqual('bar', result)

      inst = self.model_class()(dict(foo='bar'))
      result = inst.resolve_prop('bar', 'backup', None)
      self.assertEqual('backup', result)

    def test_get_prop_with_supplier(self):
      class SimpleSupplier(ValueSupplier):
        def _compute(self) -> Any:
          return 'simple'

      models_man.add_classes([SimpleSupplier])
      inst = self.model_class()(dict(
        foo=dict(kind=SimpleSupplier.__name__)
      ))

      result = inst.resolve_prop('foo', 'backup', None)
      self.assertEqual('simple', result)

    def test_get_prop_with_supplier_and_subs(self):
      class InterpolationSupplier(ValueSupplier):
        def _compute(self) -> Any:
          return '{app/ns}'

      config_man._ns = 'mock-ns'
      models_man.add_classes([InterpolationSupplier])
      inst = self.model_class()(dict(
        foo=dict(kind=InterpolationSupplier.__name__)
      ))

      result = inst.resolve_prop('foo', 'backup', None)
      self.assertEqual('mock-ns', result)

    def test_try_iftt_intercept_with_iftt_dict(self):
      models_man.clear(restore_defaults=True)
      config = dict(
        kind=Iftt.__name__,
        items=[
          dict(predicate=FalsePredicate.__name__, value='incorrect'),
          dict(predicate=TruePredicate.__name__, value='correct')
        ]
      )
      result = self.model_class().try_iftt_intercept(config, {})
      self.assertEqual('correct', result)

    def test_try_iftt_intercept_with_iftt_id(self):
      models_man.clear(restore_defaults=True)
      iftt_config = dict(
        id='my-iftt',
        kind=Iftt.__name__,
        items=[
          dict(predicate=FalsePredicate.__name__, value='incorrect'),
          dict(predicate=TruePredicate.__name__, value='correct')
        ]
      )
      models_man.add_descriptors([iftt_config])

      result = self.model_class().try_iftt_intercept('my-iftt', {})
      self.assertEqual('correct', result)

    def test_inflate_with_iftt(self):
      models_man.clear(restore_defaults=True)
      config = dict(
        kind=Iftt.__name__,
        items=[
          dict(predicate=FalsePredicate.__name__, value='incorrect'),
          dict(predicate=TruePredicate.__name__, value=dict(
            id='actual',
            title='Actual'
          ))
        ]
      )
      result = self.model_class().inflate(config, None)
      self.assertEqual('actual', result.id())
      self.assertEqual('Actual', result._title)

    def test_inflate_with_id(self):
      a, b = [g_conf(k='a', i=self.kind), g_conf(k='b', i=self.kind)]
      models_man.add_descriptors([a, b])
      inflated = self.model_class().inflate('a')
      self.assertEqual(type(inflated), self.model_class())
      self.assertEqual(inflated.id(), 'a')
      self.assertEqual(inflated._title, 'a.title')

    # def test_update_attrs(self):
    #   config = {'title': 'foo'}
    #   inflated = self.model_class().inflate_with_config(config, None, None)
    #   self.assertEqual('foo', inflated._title)
    #   inflated.update_attrs(dict(title='bar'))
    #   self.assertEqual(inflated._title, 'bar')

    def test_inflate_with_type_key(self):
      class Custom(self.model_class()):
        def __init__(self, config):
          super().__init__(config)
          self.info = 'baz'

      models_man.add_classes([Custom])
      result = self.model_class().inflate_with_key(Custom.__name__, None)
      self.assertEqual(Custom, result.__class__)
      self.assertEqual('baz', result.info)

    def test_inflate_with_config_simple(self):
      config = {'title': 'foo'}
      inflated = self.model_class().inflate_with_config(config, None, None)
      self.assertEqual('foo', inflated._title)
      self.assertEqual(self.model_class(), inflated.__class__)

    def test_inflate_with_config_inherit_easy(self):
      models_man.add_descriptors([{
        'kind': self.model_class().__name__,
        'id': 'parent',
        'title': 'yours'
      }])

      inheritor_config = {'id': 'mine', 'inherit': 'parent'}
      actual = self.model_class().inflate_with_config(inheritor_config, None, None)
      self.assertEqual(self.model_class(), actual.__class__)
      self.assertEqual('mine', actual.id())
      self.assertEqual('yours', actual._title)

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

      actual = self.model_class().inflate_with_config(inheritor_config, None, None)
      self.assertEqual(SubModel, actual.__class__)
      self.assertEqual('mine', actual.id())
      self.assertEqual('yours', actual._title)
      self.assertEqual('grandpas', actual.info)

    def test_inflate_with_config_expl_cls(self):
      class SubModel(self.model_class()):
        pass

      models_man.add_classes([SubModel])
      inheritor_config = {'id': 'mine', 'kind': SubModel.__name__}
      actual = self.model_class().inflate_with_config(inheritor_config, None, None)
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

    def test_context_inheritance(self):
      class ChildClass(WizModel):
        pass

      parent_config = dict(
        kind=self.model_class().__name__,
        id='parent',
        context=dict(parent='context'),
        bar='baz',
        children=[
          dict(
            kind=ChildClass.__name__,
            id='child',
          )
        ]
      )

      models_man.add_classes([ChildClass])
      models_man.add_descriptors([parent_config])

      parent_inst: WizModel = self.model_class().inflate('parent')
      child = parent_inst.inflate_children('children', ChildClass)[0]
      self.assertEqual(dict(parent='context'), child.context)

      child = parent_inst.inflate_children(
        'children',
        ChildClass,
        dict(more='context')
      )[0]
      self.assertEqual('context', child.config.get('more'))

      child = parent_inst.inflate_children(
        'children',
        ChildClass,
        dict(
          context=dict(
            resolvers=dict(
              extra_foo=lambda s: f"{s}-2"
            )
          )
        )
      )[0]

      child_ctx = child.assemble_eval_context(None)
      self.assertEqual(
        'bar-2',
        child_ctx.get('resolvers').get('extra_foo')('bar')
      )
