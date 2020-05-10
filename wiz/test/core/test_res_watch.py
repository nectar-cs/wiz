import yaml

from k8_kat.tests.res.common.test_kat_config_map import TestKatConfigMap
from k8_kat.tests.res.common.test_kat_dep import TestKatDep
from k8_kat.tests.res.common.test_kat_svc import TestKatSvc
from k8_kat.utils.testing import ns_factory
from wiz.core import res_watch
from wiz.core.wiz_globals import wiz_globals
from wiz.test.test_helpers.cluster_test import ClusterTest


class TestResWatch(ClusterTest):

  def test_glob_generic(self):
    ns, _ = ns_factory.request(2)
    wiz_globals.ns_overwrite = ns
    TestKatDep.create_res('dep1', ns)
    TestKatSvc.create_res('svc1', ns)
    TestKatConfigMap.create_res('map1', ns)

    result = res_watch.glob(['Deployment'])
    self.assertEqual(len(result), 1)
    self.assertEqual(result[0]['name'], 'dep1')
    self.assertIsNotNone(result[0]['updated_at'])

    result = res_watch.glob(['Deployment', 'Service', 'ConfigMap'])
    self.assertEqual(len(result), 3)
    self.assertEqual(result[0]['name'], 'dep1')
    self.assertEqual(result[1]['name'], 'svc1')
    self.assertEqual(result[2]['name'], 'map1')

  def test_glob_master_cm(self):
    ns, = ns_factory.request(1)
    wiz_globals.ns_overwrite = ns
    data = dict(master=yaml.dump(dict(foo='bar')))
    TestKatConfigMap.create_res('master', ns, data=data)
    result = res_watch.glob(['ConfigMap'])
    self.assertEqual(len(result), 1)
    self.assertEqual(result[0]['name'], 'master')
    self.assertEqual(result[0]['extras'], dict(foo='bar'))

  def tearDown(self) -> None:
    super().tearDown()
    ns_factory.relinquish_all()