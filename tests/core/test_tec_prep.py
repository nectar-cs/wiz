import yaml

from k8_kat.res.pod.kat_pod import KatPod
from tests.test_helpers.cluster_test import ClusterTest
from tests.test_helpers.helper import tec_setup

from wiz.core import tec_prep, tec_client


class TestTecPrep(ClusterTest):

  def test_create(self):
    tec_prep.create('n3', tec_setup())
    ted_pod = KatPod.find('n3', tec_prep.pod_name)
    self.assertIsNotNone(ted_pod)
    self.assertTrue(ted_pod.wait_until_running())

    out = ted_pod.shell_exec(tec_client.interpolate_cmd)
    self.assertIsNotNone(out)
    parsed = list(yaml.load_all(out, Loader=yaml.FullLoader))
    self.assertGreater(len(parsed), 0)
