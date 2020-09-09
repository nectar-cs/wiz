from typing import Type, Dict
from unittest.mock import patch

from nectwiz.core.core import config_man
from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.operations.operation_state import OperationState
from nectwiz.model.step.step import Step
from nectwiz.tests.models.test_wiz_model import Base
from nectwiz.tests.t_helpers import helper
from nectwiz.tests.t_helpers.helper import one_step_state


class TestStep(Base.TestWizModel):

  @classmethod
  def model_class(cls) -> Type[WizModel]:
    return Step

  def test_run_committing_vars(self):
    with patch.object(config_man, 'commit_keyed_tam_assigns') as mock:
      outcome = Step(dict(id='s')).run({})
      mock.assert_not_called()
      self.assertEqual('positive', outcome['status'])
      self.assertEqual({}, outcome['chart_assigns'])
      self.assertEqual({}, outcome['state_assigns'])
      self.assertEqual(None, outcome.get('job_id'))

  def test_commit_with_chart_vars(self):
    step = Step(dict(id='s', fields=[{'key': 'f1.foo'}]))
    with patch.object(config_man, 'commit_keyed_tam_assigns') as commit_mock:
      outcome = step.run({'f1.foo': 'v1'})
      self.assertEqual('positive', outcome['status'])
      self.assertEqual({'f1.foo': 'v1'}, outcome['chart_assigns'])
      self.assertEqual({}, outcome['state_assigns'])
      self.assertEqual(None, outcome.get('job_id'))
      commit_mock.assert_called_with([('f1.foo', 'v1')])

  def test_compute_recalled_assigns(self):
    step1 = Step({'id': 's1'})

    step2 = Step({
      'id': 's2',
      'reassignments': [
        {
          'target': 'chart',
          'ids': ['s1.state-var', 's2.state-var']
        },
        {
          'target': 'state',
          'ids': ['s1.chart-var', 's2.chart-var']
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
