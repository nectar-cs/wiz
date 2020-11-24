from k8kat.utils.testing import ns_factory

from nectwiz.model.action.action_parts.apply_manifest_action_part import ApplyManifestActionPart
from nectwiz.model.action.base.observer import Observer
from nectwiz.model.error.controller_error import ActionHalt
from nectwiz.tests.models.helpers import good_cmap_kao, bad_cmap_kao
from nectwiz.tests.t_helpers.cluster_test import ClusterTest


class TestActionObserver(ClusterTest):

  def test_check_kao_failures(self):
    observer = Observer()
    ns, = ns_factory.request(1)
    self.assertEqual([], observer.errdicts)
    outcomes = [*good_cmap_kao(ns), *bad_cmap_kao(ns)]

    with self.assertRaises(ActionHalt):
      ApplyManifestActionPart.check_kao_failures(observer, outcomes)

    self.assertEqual(1, len(observer.errdicts))
    errdict = observer.errdicts[0]
    print(errdict)
    self.assertEqual('manifest_apply_failed', errdict['type'])
    # self.assertEqual('apply_manifest', errdict['event_type'])
    self.assertEqual('configmaps', errdict['resource']['kind'])
    self.assertEqual('cm-bad', errdict['resource']['name'])
