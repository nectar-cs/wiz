from typing import Type

from k8kat.utils.testing import ns_factory

from nectwiz.core.core.config_man import config_man
from nectwiz.model.action.base.action import Action
from nectwiz.model.base.wiz_model import WizModel, models_man
from nectwiz.model.field.field import TARGET_CHART, TARGET_INLIN, TARGET_STATE, TARGET_PREFS
from nectwiz.model.operation.operation_state import OperationState
from nectwiz.model.operation.step import Step
from nectwiz.model.predicate.common_predicates import TruePredicate
from nectwiz.model.predicate.iftt import Iftt
from nectwiz.tests.models.test_wiz_model import Base
from nectwiz.tests.t_helpers.helper import one_step_state, create_base_master_map


class TestStep(Base.TestWizModel):

  @classmethod
  def model_class(cls) -> Type[WizModel]:
    return Step

  def test_next_step_without_iftt(self):
    op_state = OperationState('', '')
    step = Step(dict())
    self.assertIsNone(step.next_step_id(op_state))
    self.assertFalse(step.has_explicit_next())

    step = Step(dict(next=None))
    self.assertIsNone(step.next_step_id(op_state))
    self.assertFalse(step.has_explicit_next())

    step = Step(dict(next='default'))
    self.assertEqual('default', step.next_step_id(op_state))
    self.assertFalse(step.has_explicit_next())

    step = Step(dict(next='foo'))
    self.assertEqual('foo', step.next_step_id(op_state))
    self.assertTrue(step.has_explicit_next())

  def test_visible_fields(self):
    step = Step(dict(
      id='step',
      fields=[
        dict(
          id='fields.f1'
        ),
        dict(
          id='fields.f2',
          show_condition=dict(
            challenge='{input/fields.f1}',
            check_against='one'
          )
        ),
        dict(
          id='fields.f3',
          show_condition=dict(
            challenge='{operation/fields.f2}',
            check_against='two'
          )
        )
      ]
    ))

    op_state = OperationState('xxx', 'yyy')
    step_state = op_state.gen_step_state(step, keep=True)
    ids = lambda models: [m.id() for m in models]

    step_state.state_assigns = {}
    result = step.visible_fields({}, op_state)
    self.assertEqual(['fields.f1'], ids(result))

    step_state.state_assigns = {}
    result = step.visible_fields({'fields.f1': 'two'}, op_state)
    self.assertEqual(['fields.f1'], ids(result))

    step_state.state_assigns = {}
    result = step.visible_fields({'fields.f1': 'one'}, op_state)
    self.assertEqual(['fields.f1', 'fields.f2'], ids(result))

    step_state.state_assigns = {'fields.f2': 'two'}
    result = step.visible_fields({'fields.f1': 'three'}, op_state)
    self.assertEqual(['fields.f1', 'fields.f3'], ids(result))

  def test_validate_field(self):
    self.assertEqual(1, 2)  # todo fucking do this

  def test_assemble_action_config(self):
    models_man.clear(restore_defaults=True)
    models_man.add_descriptors([
      dict(id='foo', kind=Action.__name__)
    ])

    op_state = OperationState('', '')

    step = Step(dict(id='step', action='foo'))
    state = op_state.gen_step_state(step)
    result = step.assemble_action_config(state)

    expected_contains = Step.last_minute_action_config(state)
    for key, value in expected_contains.items():
      self.assertEqual(value, result.get(key))

  def test_commit_pertinent_assignments(self):
    config_man._ns, = ns_factory.request(1)
    create_base_master_map(config_man.ns())

    config_man.patch_manifest_vars({'prior': 'entry'})
    config_man.patch_prefs({'prior': 'entry'})

    buckets = {
      TARGET_CHART: {'one.two': 'three'},
      TARGET_INLIN: {'four.five': 'six'},
      TARGET_STATE: {'seven.eight': 'nine'},
      TARGET_PREFS: {'ten.eleven': 'twelve'}
    }

    Step.commit_pertinent_assignments(buckets)

    self.assertEqual(dict(
      prior='entry',
      one=dict(two='three')
    ), config_man.manifest_vars())

    self.assertEqual(dict(
      prior='entry',
      ten=dict(eleven='twelve')
    ), config_man.prefs())

  def test_next_step_with_predicate(self):
    models_man.clear(restore_defaults=True)
    step = Step(dict(
      next=dict(
        kind=Iftt.__name__,
        items=[
          dict(
            predicate=dict(
              challenge="{operation/x.y}",
              check_against='z'
            ),
            value='foo'
          ),
          dict(
            predicate=TruePredicate.__name__,
            value='bar'
          )
        ]
      )
    ))

    op_state = OperationState('', '')
    op_state.gen_step_state(step)

    self.assertTrue(step.has_explicit_next())

    op_state.step_states[0].state_assigns = {"x.y": 'z'}
    actual = step.next_step_id(op_state)
    self.assertEqual('foo', actual)

    op_state.step_states[0].state_assigns = {"x.y": 'not-z'}
    actual = step.next_step_id(op_state)
    self.assertEqual('bar', actual)

    op_state.step_states[0].state_assigns = {}
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
    man_vars = config_man.manifest_vars()
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
        {'id': 'f3', 'target': 'state'},
        {'id': 'f4', 'target': 'prefs'}
      ]
    })

    assigns = dict(
      f1='v1',
      f2='v2',
      f3='v3',
      f4='v4'
    )

    expected = dict(
      chart={'f1': 'v1'},
      inline={'f2': 'v2'},
      state={'f3': 'v3'},
      prefs={'f4': 'v4'}
    )

    actual = step.partition_flat_user_asgs(assigns, one_step_state(step))
    self.assertEqual(expected, actual)
