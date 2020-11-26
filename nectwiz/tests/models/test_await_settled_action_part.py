from k8kat.utils.testing import ns_factory

from nectwiz.core.core.config_man import config_man
from nectwiz.model.action.action_parts.await_settled_action_part import AwaitSettledActionPart
from nectwiz.model.action.base.observer import Observer
from nectwiz.model.error.controller_error import ActionHalt
from nectwiz.tests.models.helpers import bad_pod_kao, good_cmap_kao
from nectwiz.tests.t_helpers.cluster_test import ClusterTest


class TestAwaitSettledActionPart(ClusterTest):
  def test_on_await_cycle_done_no_errs(self):
    observer = Observer()
    ns, = ns_factory.request(1)
    config_man._ns = ns
    outcomes = [*good_cmap_kao(ns), *bad_pod_kao(ns)]

    perform = lambda: AwaitSettledActionPart.perform(observer, outcomes)
    self.assertRaises(ActionHalt, perform)

    self.assertEqual(1, len(observer.errdicts))
    errdict = observer.errdicts[0]

    self.assertEqual('res_settle_failed', errdict['type'])
    self.assertEqual('pod', errdict['resource']['kind'])
    self.assertEqual('pod-bad', errdict['resource']['name'])
