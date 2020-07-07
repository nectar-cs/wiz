from typing import Type
from unittest.mock import patch

from wiz.core import tedi_client, step_job_prep
from wiz.model.base.wiz_model import WizModel
from wiz.model.step.step import Step
from wiz.tests.models.test_wiz_model import Base
from wiz.tests.t_helpers import helper


class TestStep(Base.TestWizModel):

  @classmethod
  def model_class(cls) -> Type[WizModel]:
    return Step

  def test_commit_no_work(self):
    with patch.object(tedi_client, 'commit_values') as mock:
      outcome = Step(dict(key='s')).commit({})
      mock.assert_not_called()
      self.assertEqual('positive', outcome['status'])
      self.assertEqual({}, outcome['chart_assigns'])
      self.assertEqual({}, outcome['state_assigns'])
      self.assertEqual(None, outcome.get('job_id'))

  def test_commit_with_chart_vars(self):
    step = Step(dict(key='s', fields=[{'key': 'f1'}]))
    with patch.object(tedi_client, 'commit_values') as commit_mock:
      with patch.object(tedi_client, 'apply') as apply_mock:
        outcome = step.commit({'f1': 'v1'})
        self.assertEqual('pending', outcome['status'])
        self.assertEqual({'f1': 'v1'}, outcome['chart_assigns'])
        self.assertEqual(None, outcome.get('job_id'))
        commit_mock.assert_called_with({'f1': 'v1'}.items())
        apply_mock.assert_called_with(rules=[], inlines={}.items())

  def test_commit_with_job(self):
    job_desc = dict(image='foo', command=['bar'], args=['baz'])
    step = Step(dict(key='s', job=job_desc, fields=[{'key': 'f1', 'target': 'state'}]))

    with patch.object(step_job_prep, 'create_and_run') as run_mock:
      run_mock.return_value = 'id'
      outcome = step.commit(dict(f1='v1'))
      run_mock.assert_called_with('foo', ['bar'], ['baz'], {'f1': 'v1'})
      self.assertEqual('pending', outcome['status'])
      self.assertEqual('id', outcome['job_id'])

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

    actual = step.partition_value_assigns(dict(), op_state)
    self.assertEqual(({}, {}, {}), actual)
