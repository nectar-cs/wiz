from k8kat.res.config_map.kat_map import KatMap
from k8kat.utils.testing import ns_factory

from nectwiz.core.core import consts
from nectwiz.core.core.config_man import config_man
from nectwiz.model.action.action_parts.apply_manifest_action_part import ApplyManifestActionPart
from nectwiz.model.action.base.observer import Observer
from nectwiz.model.error.controller_error import ActionHalt
from nectwiz.tests.models.helpers import tam_apply_cmap, bad_cmap_kao
from nectwiz.tests.t_helpers import helper
from nectwiz.tests.t_helpers.cluster_test import ClusterTest


class TestActionObserver(ClusterTest):

  def test_perform_explicit_tam(self):
    config_man._ns, = ns_factory.request(1)
    helper.create_base_master_map(config_man._ns)
    observer = Observer()
    ApplyManifestActionPart.perform(
      observer=observer,
      values={'k': '2'},
      selectors=[],
      tam={'type': consts.virtual_tam, 'uri': helper.TrivialVirtualTam}
    )

    self.assertEqual(0, len(observer.errdicts))
    res = KatMap.find('foo', config_man.ns())
    self.assertEqual('v-2', res.data.get('k'))

  def test_check_kao_failures(self):
    ns, = ns_factory.request(1)
    observer = Observer()

    self.assertEqual([], observer.errdicts)
    outcomes = [*tam_apply_cmap(ns), *bad_cmap_kao(ns)]

    with self.assertRaises(ActionHalt):
      ApplyManifestActionPart.check_kao_failures(observer, outcomes)

    self.assertEqual(1, len(observer.errdicts))
    errdict = observer.errdicts[0]
    self.assertEqual('manifest_apply_failed', errdict['type'])
    # self.assertEqual('apply_manifest', errdict['event_type'])
    self.assertEqual('configmaps', errdict['resource']['kind'])
    self.assertEqual('cm-bad', errdict['resource']['name'])
