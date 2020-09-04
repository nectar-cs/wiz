from typing import Type, Optional

from k8kat.auth.kube_broker import broker
from k8kat.utils.testing import ns_factory
from kubernetes.client import V1ConfigMap, V1ObjectMeta

from nectwiz.core import config_man
from nectwiz.core.wiz_app import wiz_app
from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.predicate.predicate import Predicate
from nectwiz.tests.models.test_wiz_model import Base
from nectwiz.tests.t_helpers.helper import create_base_master_map


class TestPredicate(Base.TestWizModel):

  @classmethod
  def model_class(cls) -> Type[WizModel]:
    return Predicate

  def test_chart_value_compare(self):
    ns, = ns_factory.request(1)
    wiz_app._ns = ns
    create_base_master_map(ns)
    config_man.commit_keyed_tam_assigns([
      ('foo', 'bar'),
      ('x', '1')
    ])

    self.assertTrue(mk_pred3('foo', None, 'defined'))
    self.assertTrue(mk_pred3('foo', 'bar'))
    self.assertTrue(mk_pred3('x', '1'))
    self.assertTrue(mk_pred3('x', 0, 'gt'))
    self.assertTrue(mk_pred3('x', '2', 'lt'))
    self.assertTrue(mk_pred3('nope', None, 'undefined'))
    self.assertFalse(mk_pred3('nope', None, 'is-defined'))

  def test_eval_resource_count_compare(self):
    ns, = ns_factory.request(1)
    wiz_app._ns = ns
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
    wiz_app._ns = ns
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


def mk_pred1(sel, match, prop, against, op='eq'):
  return Predicate(dict(
    key='ec',
    selector=f'ConfigMap:{sel}',
    type='resource-property-compare',
    op=op,
    match=match,
    property=prop,
    check_against=against
  )).evaluate()


def mk_pred2(sel, against, op='eq'):
  return Predicate(dict(
    key='ec',
    selector=f'ConfigMap:{sel}',
    type='resource-count-compare',
    op=op,
    check_against=against
  )).evaluate()


def mk_pred3(variable_name, against, op: Optional[str] = 'eq'):
  return Predicate(dict(
    key='ec',
    type='chart-value-compare',
    op=op,
    variable=variable_name,
    check_against=against
  )).evaluate()

def create_cmap(name, ns=None, data=None):
  data = data if data else dict(foo='bar')
  return broker.coreV1.create_namespaced_config_map(
    namespace=ns,
    body=V1ConfigMap(
      metadata=V1ObjectMeta(name=name),
      data=data
    )
  )
