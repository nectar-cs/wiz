from typing import Type, Optional

from k8kat.auth.kube_broker import broker
from k8kat.utils.testing import ns_factory
from kubernetes.client import V1ConfigMap, V1ObjectMeta

from nectwiz.core.core import config_man
from nectwiz.core.core.config_man import config_man
from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.pre_built.common_predicates import ManifestVariablePredicate, ResourceCountPredicate, \
  ResourcePropertyPredicate, MultiPredicate
from nectwiz.model.predicate.predicate import Predicate
from nectwiz.tests.models.test_wiz_model import Base
from nectwiz.tests.t_helpers.helper import create_base_master_map


class TestPredicate(Base.TestWizModel):

  @classmethod
  def model_class(cls) -> Type[WizModel]:
    return Predicate

  def test_test_inflate_all(self):
    super().test_inflate_all()

  def test_load_children(self):
    super().test_load_children()

  def test_base(self):
    actual = Predicate(dict(
      check_against='x',
      challenge='x'
    )).evaluate({})
    self.assertTrue(actual)

    actual = Predicate(dict(
      check_against='x',
      challenge='x'
    )).evaluate(dict(value='y'))
    self.assertFalse(actual)

    actual = Predicate(dict(
      check_against='x',
      challenge='y'
    )).evaluate(dict(value='x'))
    self.assertTrue(actual)

  def test_chart_value_compare(self):
    ns, = ns_factory.request(1)
    config_man._ns = ns
    create_base_master_map(ns)
    config_man.commit_keyed_mfst_vars([('foo', 'bar'), ('x', '1')])

    self.assertTrue(mk_pred3('foo', None, 'defined'))
    self.assertTrue(mk_pred3('foo', 'bar'))
    self.assertTrue(mk_pred3('x', '1'))
    self.assertTrue(mk_pred3('x', 0, 'gt'))
    self.assertTrue(mk_pred3('x', '2', 'lt'))
    self.assertTrue(mk_pred3('nope', None, 'undefined'))
    self.assertFalse(mk_pred3('nope', None, 'is-defined'))

  def test_eval_resource_count_compare(self):
    ns, = ns_factory.request(1)
    config_man._ns = ns
    create_cmap('r1', ns)
    create_cmap('r2', ns)

    self.assertTrue(mk_pred2('r1', 1, '='))
    self.assertTrue(mk_pred2('r1', 1, 'gte'))
    self.assertTrue(mk_pred2('r1', 2, '!='))
    self.assertTrue(mk_pred2('r1', 0, '>'))
    self.assertTrue(mk_pred2('r1', 2, '<'))
    self.assertTrue(mk_pred2('r1', 1, 'lte'))
    self.assertTrue(mk_pred2('*', 2, 'equals'))
    self.assertFalse(mk_pred2('r1', 2))

  def test_eval_resource_property_compare(self):
    ns, = ns_factory.request(1)
    config_man._ns = ns
    create_cmap('r1', ns)
    create_cmap('r2', ns)

    self.assertTrue(mk_pred1('r1', 'all', 'sig', 'ConfigMap:r1'))
    self.assertTrue(mk_pred1('*', 'any', 'name', 'r1'))
    self.assertTrue(mk_pred1('*', 'all', 'has_settled', 'True'))
    self.assertTrue(mk_pred1('*', 'all', 'raw.metadata.namespace', ns))
    self.assertFalse(mk_pred1('r2', 'all', 'name', 'r1'))
    self.assertFalse(mk_pred1('*', 'any', 'bad-prop-name', 'irrelevant'))
    self.assertFalse(mk_pred1('*', 'any', 'ternary_status', 'positive', 'neq'))
    self.assertFalse(mk_pred1('*', 'bad-matcher', 'name', 'r1'))

  def test_multi_predicate(self):
    true_pred = mk_pred0('foo', 'foo')
    false_pred = mk_pred0('foo', 'bar')
    multi = MultiPredicate(dict(
      operator='and',
      sub_predicates=[true_pred, false_pred]
    ))
    self.assertFalse(multi.evaluate({}))

    multi = MultiPredicate(dict(
      operator='or',
      sub_predicates=[false_pred, true_pred]
    ))
    self.assertTrue(multi.evaluate({}))


def mk_pred0(challenge, against, op='eq'):
  return dict(
    operator=op,
    challenge=challenge,
    check_against=against
  )


def mk_pred1(sel, match, prop, against, op='eq'):
  return ResourcePropertyPredicate(dict(
    selector=f'ConfigMap:{sel}',
    operator=op,
    match=match,
    property=prop,
    check_against=against
  )).evaluate({})


def mk_pred2(sel, against, op='eq'):
  return ResourceCountPredicate(dict(
    key='ec',
    selector=f'ConfigMap:{sel}',
    operator=op,
    check_against=against
  )).evaluate({})


def mk_pred3(variable_name, against, op: Optional[str] = 'eq'):
  return ManifestVariablePredicate(dict(
    operator=op,
    variable=variable_name,
    check_against=against
  )).evaluate({})


def create_cmap(name, ns=None, data=None):
  data = data if data else dict(foo='bar')
  return broker.coreV1.create_namespaced_config_map(
    namespace=ns,
    body=V1ConfigMap(
      metadata=V1ObjectMeta(name=name),
      data=data
    )
  )
