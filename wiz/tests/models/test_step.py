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
    op_state = helper.one_step_op_state(sass=dict(a='a', b='b', c='c'))
    recall_one = dict(target='chart', included_keys='all', excluded_keys=['b'])
    recall_two = dict(target='inline', included_keys=['a', 'b'], excluded_keys=['b'])
    step = Step(dict(key='s', state_recalls=[recall_one, recall_two]))

    chart_actual = step.compute_recalled_assigns('chart', op_state)
    inline_actual = step.compute_recalled_assigns('inline', op_state)

    self.assertEqual(dict(a='a', c='c'), chart_actual)
    self.assertEqual(dict(a='a'), inline_actual)


  def test_partition_value_assigns(self):
    chart_field = dict(key='f1', target='chart')
    inline_field = dict(key='f2', target='inline')
    state_field = dict(key='f3', target='state')

    step = Step(dict(key='s', fields=[chart_field, inline_field, state_field]))
    op_state = helper.one_step_op_state()
    actual = step.partition_value_assigns(dict(f1='v1', f2='v2', f3='v3'), op_state)
    self.assertEqual(({'f1': 'v1'}, {'f2': 'v2'}, {'f3': 'v3'}), actual)




def names(res_list):
  return [r.name for r in res_list]