from k8kat.utils.testing import ns_factory

from nectwiz.core.core.config_man import config_man
from nectwiz.model.action.action_parts.await_predicates_settle_action_part import AwaitPredicatesSettleActionPart
from nectwiz.model.action.base.observer import Observer
from nectwiz.model.error.controller_error import ActionHalt
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

    success = AwaitPredicatesSettleActionPart.perform(observer, outcomes)
    self.assertTrue(success)
    self.assertEqual(0, len(observer.errdicts))


  def test_await_settled_done_with_errors(self):
    observer = Observer()
    config_man._ns, = ns_factory.request(1)
    outcomes = [
      *tam_apply_cmap(config_man.ns()),
      *tam_apply_pod(ns=config_man.ns(), image='bad-image-09725')
    ]

    with self.assertRaises(ActionHalt):
      success = AwaitPredicatesSettleActionPart.perform(observer, outcomes)
      self.assertFalse(success)
      self.assertEqual(1, len(observer.errdicts))

      errdict = observer.errdicts[0]
      self.assertEqual('res_settle_failed', errdict['type'])
      self.assertEqual('pod', errdict['resource']['kind'])
      self.assertEqual('pod-bad', errdict['resource']['name'])
