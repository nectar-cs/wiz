from typing import Type, Dict
from unittest.mock import patch

from nectwiz.core import step_job_prep
from nectwiz.core.core import config_man
from nectwiz.core.telem.ost import OperationState, StepState
from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.stage.stage import Stage
from nectwiz.model.step.step import Step
from nectwiz.tests.models.test_wiz_model import Base
from nectwiz.tests.t_helpers import helper


class TestStep(Base.TestWizModel):

  @classmethod
  def model_class(cls) -> Type[WizModel]:
    return Step

  def test_integration(self):
    pass

  def test_own_state(self):
    op_state = OperationState(
      step_states=[
        mk_step_state('stage1', 'step1', {'k': 11}),
        mk_step_state('stage1', 'step2', {'k': 12}),
        mk_step_state('stage2', 'step1', {'k': 21}),
        mk_step_state('stage2', 'step2', {'k': 22}),
      ]
    )

    stage = Stage(dict(key='stage2', steps=[dict(key='step2')]))
    step: Step = stage.step('step2')
    step_state = step.find_own_state(op_state)
    self.assertEqual('stage2', step_state.stage_id)
    self.assertEqual('step2', step_state.step_id)
    self.assertEqual({'k': 22}, step_state.chart_assigns)

  def test_commit_no_work(self):
    with patch.object(config_man, 'commit_keyed_tam_assigns') as mock:
      outcome = Step(dict(key='s')).run({})
      mock.assert_not_called()
      self.assertEqual('positive', outcome['status'])
      self.assertEqual({}, outcome['chart_assigns'])
      self.assertEqual({}, outcome['state_assigns'])
      self.assertEqual(None, outcome.get('job_id'))

  def test_commit_with_chart_vars(self):
    step = Step(dict(key='s', fields=[{'key': 'f1.foo'}]))
    with patch.object(config_man, 'commit_keyed_tam_assigns') as commit_mock:
      outcome = step.run({'f1.foo': 'v1'})
      self.assertEqual('positive', outcome['status'])
      self.assertEqual({'f1.foo': 'v1'}, outcome['chart_assigns'])
      self.assertEqual({}, outcome['state_assigns'])
      self.assertEqual(None, outcome.get('job_id'))
      commit_mock.assert_called_with([('f1.foo', 'v1')])

  def test_commit_with_job(self):
    job_desc = dict(image='foo', command=['bar'], args=['baz'])
    field_desc = {'key': 'f1', 'target': 'state'}
    step = Step(dict(key='s', job=job_desc, fields=[field_desc]))

    with patch.object(step_job_prep, 'create_and_run') as run_mock:
      run_mock.return_value = 'id'
      outcome = step.run(dict(f1='v1'))
      run_mock.assert_called_with('foo', ['bar'], ['baz'], {'f1': 'v1'})
      self.assertEqual('pending', outcome['status'])
      self.assertEqual('id', outcome['job_id'])

  def test_compute_recalled_assigns(self):
    step_state = dict(a='a', b='b', c='c')
    op_state = helper.one_step_op_state(sass=step_state)
    recall_one = mk_recall('chart', 'all', ['b'])
    recall_two = mk_recall('inline', ['a', 'b'], ['b'])
    step = Step(dict(key='s', state_recalls=[recall_one, recall_two]))

    chart_actual = step.compute_recalled_assigns('chart', op_state)
    inline_actual = step.compute_recalled_assigns('inline', op_state)

    self.assertEqual(dict(a='a', c='c'), chart_actual)
    self.assertEqual(dict(a='a'), inline_actual)

  def test_partition_value_assigns(self):
    chart_field = dict(key='f1', target='chart')
    inline_field = dict(key='f2', target='inline')
    state_field = dict(key='f3', target='state')
    fields = [chart_field, inline_field, state_field]

    step = Step(dict(key='s', fields=fields))
    op_state = helper.one_step_op_state()
    assign = dict(f1='v1', f2='v2', f3='v3')
    actual = step.partition_user_asgs(assign, op_state)
    self.assertEqual(({'f1': 'v1'}, {'f2': 'v2'}, {'f3': 'v3'}), actual)

    actual = step.partition_user_asgs(dict(), op_state)
    self.assertEqual(({}, {}, {}), actual)


def mk_recall(target, inc_keys, exc_keys) -> Dict:
  return dict(target=target, included_keys=inc_keys, excluded_keys=exc_keys)


def mk_step_state(stage_id, step_id, chart_assigns) -> StepState:
  return StepState(
    stage_id=stage_id,
    step_id=step_id,
    commit_outcome=dict(chart_assigns=chart_assigns)
  )
