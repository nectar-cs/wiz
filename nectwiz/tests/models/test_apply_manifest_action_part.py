import time

from k8kat.utils.testing import ns_factory

from nectwiz.core.core import utils
from nectwiz.core.core.config_man import config_man
from nectwiz.core.core.types import KAOs
from nectwiz.core.tam.tam_client import TamClient
from nectwiz.model.action.action_parts.apply_manifest_action_part import ApplyManifestActionPart
from nectwiz.model.action.base.observer import Observer
from nectwiz.model.error.controller_error import ActionHalt
from nectwiz.model.operation import status_computer
from nectwiz.model.operation.step_state import StepState
from nectwiz.tests.models.helpers import good_cmap_kao, bad_cmap_kao
from nectwiz.tests.t_helpers.cluster_test import ClusterTest


class TestActionObserver(ClusterTest):

  def test_check_kao_failures(self):
    subject = ApplyManifestActionPart
    observer = Observer()
    ns, = ns_factory.request(1)
    self.assertEqual([], observer.errdicts)
    outcomes = [*good_cmap_kao(ns), *bad_cmap_kao(ns)]

    with self.assertRaises(ActionHalt):
      subject.check_kao_failures(observer, outcomes)

    self.assertEqual(1, len(observer.errdicts))
    errdict = observer.errdicts[0]
    self.assertEqual('apply_manifest', errdict['event_type'])
    self.assertEqual('configmaps', errdict['resource']['kind'])
    self.assertEqual('cm-bad', errdict['resource']['name'])


