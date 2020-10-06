from unittest.mock import patch

from nectwiz.model.operation.operation_state import OperationState
from nectwiz.model.predicate.predicate import Predicate
from nectwiz.model.operation.status_computer import eval_preds, compute
from nectwiz.model.operation.step import Step
from nectwiz.tests.t_helpers.cluster_test import ClusterTest


class TestStatusComputer(ClusterTest):

  def test_eval_preds_halting_logic(self):
    step_state = OperationState('', '').gen_step_state(Step({}))
    predicates = [TrivPred({'id': 'x', 'o': True}), TrivPred({})]
    eval_preds(predicates, 'negative', step_state, {})
    exp_eval = {'met': True, 'name': 'x', 'predicate_id': 'x', 'reason': 'r'}
    exp = {'positive': [], 'negative': [exp_eval]}
    self.assertEqual(exp, step_state.exit_statuses)

  def test_eval_preds_recycle_logic(self):
    step_state = OperationState('', '').gen_step_state(Step({}))
    cached_result = {'predicate_id': 'x', 'met': True}
    step_state.exit_statuses = {'positive': [cached_result], 'negative': []}
    eval_preds([TrivPred({'id': 'x'})], 'positive', step_state, {})

  def test_eval_preds_recomputing_logic(self):
    step_state = OperationState('', '').gen_step_state(Step({}))
    cached_result = {'predicate_id': 'x', 'met': False}
    step_state.exit_statuses = {'positive': [cached_result], 'negative': []}
    predicate = TrivPred({'id': 'x', 'o': True})
    eval_preds([predicate], 'positive', step_state, {})
    exp_eval = {'predicate_id': 'x', 'met': True, 'name': 'x', 'reason': 'r'}
    exp = {'positive': [exp_eval], 'negative': []}
    self.assertEqual(exp, step_state.exit_statuses)

  def test_compute_empty(self):
    step_state = OperationState('', '').gen_step_state(Step({}))
    compute({}, step_state, {})
    self.assertTrue(step_state.did_succeed())
    compute({'positive': [], 'negative': []}, step_state, {})
    self.assertTrue(step_state.did_succeed())


class TrivPred(Predicate):
  def __init__(self, config=None):
    config['title'] = config.get('id')
    super().__init__(config or {})
    self.outcome = (config or {}).get('o', False)
    self.reason = 'r'

  def evaluate(self, context):
    return self.outcome
