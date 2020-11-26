from typing import Type, Any, List, Tuple

from nectwiz.core.core.config_man import config_man
from nectwiz.model.base.wiz_model import WizModel, models_man
from nectwiz.model.operation.field import Field
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

    @classmethod
    def has_many_tuples(cls) -> List[Tuple[str, Type]]:
      return []

    @property
    def kind(self) -> str:
      return self.model_class().__name__

    def test_has_many_associations(self):
      inst = self.model_class()({})
      for (prop, cls) in self.has_many_tuples():
        inst.inflate_children(cls, prop=prop)

    def test_try_as_iftt_when_not_iftt(self):
      config = dict(kind=self.model_class().kind(), id='foo')
      result = self.model_class().try_iftt_intercept(kod=config)
      self.assertEqual(config, result)

    def test_get_prop_default(self):
      inst = self.model_class()(dict(foo='bar'))
      result = inst.get_prop('foo', 'backup')
      self.assertEqual('bar', result)

      inst = self.model_class()(dict(foo='bar'))
      result = inst.get_prop('bar', 'backup')
      self.assertEqual('backup', result)

    def test_get_prop_with_supplier(self):
      class SimpleSupplier(ValueSupplier):
        def _compute(self) -> Any:
          return 'simple'

      models_man.add_classes([SimpleSupplier])
      inst = self.model_class()(dict(
        foo=dict(kind=SimpleSupplier.__name__)
      ))

      result = inst.get_prop('foo', 'backup')
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

      result = inst.get_prop('foo', 'backup')
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
      result = self.model_class().try_iftt_intercept(kod=config)
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

      result = self.model_class().try_iftt_intercept(kod='my-iftt')
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
      self.assertEqual('Actual', result.title)

    def test_inflate_with_id(self):
      a, b = [g_conf(k='a', i=self.kind), g_conf(k='b', i=self.kind)]
      models_man.add_descriptors([a, b])
      inflated = self.model_class().inflate('a')
      self.assertEqual(type(inflated), self.model_class())
      self.assertEqual(inflated.id(), 'a')
      self.assertEqual(inflated.title, 'a.title')

    def test_update_attrs(self):
      config = {'title': 'foo'}
      inflated = self.model_class().inflate(config)
      self.assertEqual('foo', inflated.title)
      inflated.update_attrs(dict(title='bar'))
      self.assertEqual(inflated.title, 'bar')

    def test_inflate_with_type_key(self):
      class Custom(self.model_class()):
        @property
        def info(self):
          return 'baz'

      models_man.add_classes([Custom])
      result = self.model_class().inflate_with_id(Custom.__name__, None)
      self.assertEqual(Custom, result.__class__)
      self.assertEqual('baz', result.info)

    def test_inflate_with_config_simple(self):
      inflated = self.model_class().inflate({'title': 'foo'})
      self.assertEqual('foo', inflated.title)
      self.assertEqual(self.model_class(), inflated.__class__)

    def test_inflate_with_config_inherit_easy(self):
      models_man.add_descriptors([{
        'kind': self.model_class().__name__,
        'id': 'parent',
        'title': 'yours'
      }])

      inheritor_config = {'id': 'mine', 'inherit': 'parent'}
      actual = self.model_class().inflate(inheritor_config)
      self.assertEqual(self.model_class(), actual.__class__)
      self.assertEqual('mine', actual.id())
      self.assertEqual('yours', actual.title)

    def test_inflate_with_config_inherit_hard(self):
      class DonorModel(self.model_class()):
        pass

      donor_config = {
        'kind': DonorModel.__name__,
        'id': 'donor-id',
        'title': 'donor-title',
        'info': 'donor-info'
      }

      inheritor_config = {
        'id': 'inheritor-id',
        'inherit': 'donor-id',
        'title': 'inheritor-title',
      }

      models_man.add_classes([DonorModel])
      models_man.add_descriptors([donor_config])

      inheritor = self.model_class().inflate(inheritor_config)
      self.assertEqual(DonorModel, inheritor.__class__)
      self.assertEqual('inheritor-id', inheritor.id())
      self.assertEqual('inheritor-title', inheritor.title)
      self.assertEqual('donor-info', inheritor.info)

    def test_inflate_with_config_expl_cls(self):
      class SubModel(self.model_class()):
        pass

      models_man.add_classes([SubModel])
      inheritor_config = {'id': 'mine', 'kind': SubModel.__name__}
      actual = self.model_class().inflate(inheritor_config)
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
      result = parent_inst.inflate_children(ChildClass, prop='children')
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
      child = parent_inst.inflate_children(ChildClass, prop='children')[0]
      self.assertEqual(dict(parent='context'), child.context)

      child = parent_inst.inflate_children(
        ChildClass,
        prop='children',
        patches=dict(more='context')
      )[0]
      self.assertEqual('context', child.config.get('more'))

      child = parent_inst.inflate_children(
        ChildClass,
        prop='children',
        patches=dict(
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
