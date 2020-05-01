import yaml

from k8_kat.res.pod.kat_pod import KatPod
from k8_kat.utils.testing import ns_factory
from tests.test_helpers.cluster_test import ClusterTest
from tests.test_helpers.helper import tec_setup, create_base_master_map

from wiz.core import tec_prep, tec_client


class TestTecPrep(ClusterTest):

  @classmethod
  def setUpClass(cls) -> None:
    super(TestTecPrep, cls).setUpClass()
    cls.ns, = ns_factory.request(1)

  @classmethod
  def tearDownClass(cls) -> None:
    ns_factory.relinquish_all()
    pass

  def test_create(self):
    create_base_master_map(self.ns)
    tec_prep.create(self.ns, tec_setup())

    ted_pod = KatPod.find(tec_prep.pod_name, self.ns)
    self.assertIsNotNone(ted_pod)
    self.assertTrue(ted_pod.wait_until(ted_pod.is_running, 360))

    out = ted_pod.shell_exec(tec_client.interpolate_cmd)
    self.assertIsNotNone(out)
    parsed = list(yaml.load_all(out, Loader=yaml.FullLoader))
    self.assertGreater(len(parsed), 0)

