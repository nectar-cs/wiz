from typing import Type

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

  def test_eval_resource_property_compare(self):
    ns, = ns_factory.request(1)
    wiz_app.ns_overwrite = ns
    TestKatConfigMap.create_res('r1', ns)
    TestKatConfigMap.create_res('r2', ns)

    self.assertTrue(mk_pred1('r1', 'all', 'sig', 'ConfigMap:r1'))
    self.assertTrue(mk_pred1('*', 'any', 'name', 'r1'))
    self.assertTrue(mk_pred1('*', 'all', 'has_settled', 'True'))
    self.assertTrue(mk_pred1('*', 'all', 'raw.metadata.namespace', ns))
    self.assertFalse(mk_pred1('r2', 'all', 'name', 'r1'))
    self.assertFalse(mk_pred1('*', 'any', 'bad-prop-name', 'irrelevant'))
    self.assertFalse(mk_pred1('*', 'any', 'ternary_status', 'positive', 'neq'))


def mk_pred1(sel, match, prop, against, op='eq'):
  return Predicate(dict(
    key='ec',
    selector=f'ConfigMap:{sel}',
    op=op,
    match=match,
    property=prop,
    check_against=against
  )).evaluate()
