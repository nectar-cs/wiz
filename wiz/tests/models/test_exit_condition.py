from typing import Type

from k8_kat.tests.res.common.test_kat_config_map import TestKatConfigMap
from k8_kat.utils.testing import ns_factory
from wiz.core.wiz_globals import wiz_app
from wiz.model.base.wiz_model import WizModel
from wiz.model.step.exit_condition import ExitCondition
from wiz.tests.models.test_wiz_model import Base


class TestStep(Base.TestWizModel):

  @classmethod
  def model_class(cls) -> Type[WizModel]:
    return ExitCondition

  def test_eval_ternary_statuses_homogeneous(self):
    ns, = ns_factory.request(1)
    wiz_app.ns_overwrite = ns
    TestKatConfigMap.create_res('r1', ns)
    TestKatConfigMap.create_res('r2', ns)

    ec1 = mk_cond('ConfigMap:r1', 'all', 'sig', 'ConfigMap:r1')
    ec2 = mk_cond('ConfigMap:r2', 'all', 'name', 'r1')
    ec3 = mk_cond('ConfigMap:*', 'any', 'name', 'r1')
    ec4 = mk_cond('ConfigMap:*', 'all', 'has_settled', 'True')

    self.assertTrue(ec1.evaluate())
    self.assertFalse(ec2.evaluate())
    self.assertTrue(ec3.evaluate())
    self.assertTrue(ec4.evaluate())


def mk_cond(sel, match, prop, against):
  return ExitCondition(dict(
    key='ec',
    selector=sel,
    match=match,
    property=prop,
    check_against=against
  ))


