import json
from typing import Type, Optional

from k8_kat.tests.res.common.test_kat_config_map import TestKatConfigMap
from k8_kat.utils.testing import ns_factory
from wiz.core.wiz_globals import wiz_app
from wiz.model.base.wiz_model import WizModel
from wiz.model.predicate.predicate import Predicate
from wiz.tests.models.test_wiz_model import Base


class TestPredicate(Base.TestWizModel):

  @classmethod
  def model_class(cls) -> Type[WizModel]:
    return Predicate

  def test_chart_value_compare(self):
    ns, = ns_factory.request(1)
    wiz_app.ns = ns
    TestKatConfigMap.create_res('master', ns, dict(
      master=json.dumps(dict(foo='bar', x=1))
    ))
    self.assertTrue(mk_pred3('foo', None, 'defined'))
    self.assertTrue(mk_pred3('foo', 'bar'))
    self.assertTrue(mk_pred3('x', '1'))
    self.assertTrue(mk_pred3('x', 0, 'gt'))
    self.assertTrue(mk_pred3('x', '2', 'lt'))
    self.assertTrue(mk_pred3('nope', None, 'undefined'))
    self.assertFalse(mk_pred3('nope', None, 'is-defined'))

  def test_eval_resource_count_compare(self):
    ns, = ns_factory.request(1)
    wiz_app.ns = ns
    TestKatConfigMap.create_res('r1', ns)
    TestKatConfigMap.create_res('r2', ns)

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
    wiz_app.ns = ns
    TestKatConfigMap.create_res('r1', ns)
    TestKatConfigMap.create_res('r2', ns)

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