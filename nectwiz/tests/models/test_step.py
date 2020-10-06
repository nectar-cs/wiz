from typing import Type

from k8kat.utils.testing import ns_factory

from nectwiz.core.core.config_man import config_man
from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.operation.operation_state import OperationState
from nectwiz.model.operation.step import Step
from nectwiz.tests.models.test_wiz_model import Base
from nectwiz.tests.t_helpers.helper import one_step_state, create_base_master_map


def fake_assigns():
  return True


class TestStep(Base.TestWizModel):

  @classmethod
  def model_class(cls) -> Type[WizModel]:
    return Step

  def test_next_step_trivial(self):
    op_state = OperationState('', '')
    step = Step(dict())
    self.assertIsNone(step.next_step_id(op_state))

    step = Step(dict(next=None))
    self.assertIsNone(step.next_step_id(op_state))

    step = Step(dict(next='default'))
    self.assertIsNone(step.next_step_id(op_state))

    step = Step(dict(next='foo'))
    self.assertEqual('foo', step.next_step_id(op_state))

  def test_next_step_with_predicate(self):
    step = Step(dict(
      next={
        'if': dict(
          challenge="{operation/x.y}",
          check_against='z'
        ),
        'then': 'foo',
        'else': 'bar'
      }
    ))

    op_state = OperationState('', '')
    op_state.gen_step_state(step)

    op_state.step_states[0].state_assigns = {"x.y": 'z'}
    actual = step.next_step_id(op_state)
    self.assertEqual('foo', actual)

    op_state.step_states[0].state_assigns = {"x.y": 'z2'}
    actual = step.next_step_id(op_state)
    self.assertEqual('bar', actual)

  def test_run_commit_man_only(self):
    config_man._ns, = ns_factory.request(1)
    create_base_master_map(config_man.ns())
    step = Step({
      'fields': [
        {'id': 's1.f1', 'target': 'chart'},
      ]
    })

    op_state = OperationState('123', 'abc')
    step_state = op_state.gen_step_state(step)
    step.run({'s1.f1': 'foo'}, step_state)
    man_vars = config_man.read_manifest_vars()
    self.assertEqual({'s1': {'f1': 'foo'}}, man_vars)
    self.assertEqual({'s1.f1': 'foo'}, step_state.chart_assigns)
    self.assertEqual({}, step_state.state_assigns)

  def test_compute_recalled_assigns(self):
    step1 = Step({'id': 's1'})

    step2 = Step({
      'id': 's2',
      'reassignments': [
        {
          'to': 'chart',
          'id': 's1.state-var'
        },
        {
          'to': 'chart',
          'id': 's2.state-var'
        },
        {
          'to': 'state',
          'id': 's1.chart-var'
        },
        {
          'to': 'state',
          'id': 's2.chart-var'
        }
      ]
    })

    op_state = OperationState('123', 'abc')
    ss1 = op_state.gen_step_state(step1)
    ss2 = op_state.gen_step_state(step2)

    ss1.chart_assigns = {'s1.chart-var': 'v11'}
    ss1.state_assigns = {'s1.state-var': 'v12'}

    ss2.chart_assigns = {'s2.chart-var': 'v21'}
    ss2.state_assigns = {'s2.state-var': 'v22'}

    result_chart = step2.comp_recalled_asgs('chart', ss2)
    exp_chart = {'s1.state-var': 'v12', 's2.state-var': 'v22'}
    self.assertEqual(exp_chart, result_chart)

    result_state = step2.comp_recalled_asgs('state', ss2)
    exp_state = {'s1.chart-var': 'v11', 's2.chart-var': 'v21'}
    self.assertEqual(exp_state, result_state)

  def test_partition_user_asgs_no_recall(self):
    step = Step({
      'fields': [
        {'id': 'f1', 'target': 'chart'},
        {'id': 'f2', 'target': 'inline'},
        {'id': 'f3', 'target': 'state'}
      ]
    })

    assigns = dict(f1='v1', f2='v2', f3='v3')
    exp = dict(chart={'f1': 'v1'}, inline={'f2': 'v2'}, state={'f3': 'v3'})
    actual = step.partition_user_asgs(assigns, one_step_state(step))
    self.assertEqual(exp, actual)
