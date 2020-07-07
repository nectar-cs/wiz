from typing import Type

from k8_kat.tests.res.common.test_kat_config_map import TestKatConfigMap
from k8_kat.utils.testing import ns_factory
from wiz.core.wiz_globals import wiz_app
from wiz.model.base.wiz_model import WizModel
from wiz.model.step.exit_condition import ExitCondition, eval_ternary_statuses
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

    all_pos = eval_ternary_statuses('ConfigMap:*', 'all', 'positive')
    any_pos = eval_ternary_statuses('ConfigMap:*', 'any', 'positive')
    all_neg = eval_ternary_statuses('ConfigMap:*', 'all', 'negative')
    any_neg = eval_ternary_statuses('ConfigMap:*', 'any', 'negative')

    self.assertTrue(all_pos)
    self.assertTrue(any_pos)
    self.assertFalse(all_neg)
    self.assertFalse(any_neg)
