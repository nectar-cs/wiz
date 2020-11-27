from k8kat.utils.testing import ns_factory

from nectwiz.core.core.config_man import config_man
from nectwiz.model.action.action_parts.await_predicates_settle_action_part import AwaitPredicatesSettleActionPart
from nectwiz.model.action.base.observer import Observer
from nectwiz.model.error.controller_error import ActionHalt
from nectwiz.model.factory.predicate_factories import PredicateFactory
from nectwiz.tests.models.helpers import tam_apply_pod, tam_apply_cmap
from nectwiz.tests.t_helpers.cluster_test import ClusterTest


class TestAwaitSettledActionPart(ClusterTest):
  def test_on_await_cycle_done_no_errs(self):
    observer = Observer()
    config_man._ns, = ns_factory.request(1)
    outcomes = [
      *tam_apply_cmap(config_man.ns()),
      *tam_apply_pod(ns=config_man.ns())
    ]

    predicates = PredicateFactory.from_apply_outcome(outcomes)
    AwaitPredicatesSettleActionPart.perform(observer, predicates)
    self.assertEqual(0, len(observer.errdicts))

  def test_await_settled_done_with_errors(self):
    observer = Observer()
    config_man._ns, = ns_factory.request(1)
    outcomes = [
      *tam_apply_cmap(config_man.ns()),
      *tam_apply_pod(
        ns=config_man.ns(),
        name='bad-pod',
        image='bad-image-09725'
      )
    ]

    predicates = PredicateFactory.from_apply_outcome(outcomes)
    self.assertRaises(
      ActionHalt,
      lambda: AwaitPredicatesSettleActionPart.perform(observer, predicates)
    )
    self.assertEqual(1, len(observer.errdicts))

    errdict = observer.errdicts[0]

    self.assertEqual('bad-pod', errdict['resource']['name'])
    self.assertEqual('pod', errdict['resource']['kind'])
    self.assertEqual('Predicate', errdict['extras']['predicate_kind'])
    self.assertEqual('pod/bad-pod-negative', errdict['extras']['predicate_id'])
    self.assertEqual('preds_settle_failed', errdict['type'])
