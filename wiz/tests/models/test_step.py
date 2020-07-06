from typing import Type

from k8_kat.res.pod.kat_pod import KatPod


from k8_kat.utils.testing import ns_factory
from wiz.core.osr import OperationState, StepState
from wiz.core.wiz_globals import wiz_app
from wiz.model.base.wiz_model import WizModel
from wiz.model.step.step import Step
from wiz.tests.models.test_wiz_model import Base
from wiz.tests.t_helpers import helper


class TestStep(Base.TestWizModel):

  @classmethod
  def model_class(cls) -> Type[WizModel]:
    return Step

  def test_compute_recalled_assigns(self):
    recall_descriptors = [
      dict(target='chart', included_keys='all', excluded_keys=['b']),
      dict(target='inline', included_keys=['a, b'], excluded_keys=['b'])
    ]

    op_state = helper.one_step_op_state(sass=dict(a='a', b='b', c='c'))
    step = Step(dict(key='s', state_recalls=recall_descriptors))
    chart_actual = step.compute_recalled_assigns('chart', op_state)
    inline_actual = step.compute_recalled_assigns('inline', op_state)

    self.assertEqual(dict(a='a', b='b'), chart_actual)
    self.assertEqual(dict(a='a'), inline_actual)


def names(res_list):
  return [r.name for r in res_list]