import json

from k8_kat.tests.res.common.test_kat_svc import TestKatSvc

from k8_kat.tests.res.common.test_kat_config_map import TestKatConfigMap
from k8_kat.tests.res.common.test_kat_dep import TestKatDep
from k8_kat.tests.res.common.test_kat_svc import TestKatSvc
from k8_kat.utils.testing import ns_factory
from tests.test_helpers.cluster_test import ClusterTest
from wiz.core import res_watch
from wiz.core.wiz_globals import wiz_globals


class TestResWatch(ClusterTest):

  def test_glob_generic(self):
    ns, _ = ns_factory.request(2)
    wiz_globals.ns_overwrite = ns
    TestKatDep.create_res('dep1', ns)
    TestKatSvc.create_res('svc1', ns)
    TestKatConfigMap.create_res('map1', ns)

    self.assertEqual(res_watch.glob(['Deployment']),
      [{'kind': 'Deployment', 'name': 'dep1', 'status': 'pending', 'extras': {}}]
    )

    self.assertEqual(res_watch.glob(['Deployment', 'Service', 'ConfigMap']),
      [
        {'kind': 'Deployment', 'name': 'dep1', 'status': 'pending', 'extras': {}},
        {'kind': 'Service', 'name': 'svc1', 'status': 'positive', 'extras': {}},
        {'kind': 'ConfigMap', 'name': 'map1', 'status': 'positive', 'extras': {}}
      ]
    )

  def test_glob_master_cm(self):
    ns, = ns_factory.request(1)
    wiz_globals.ns_overwrite = ns
    TestKatConfigMap.create_res('master', ns, data=dict(master=json.dumps(dict(foo='bar'))))
    self.assertEqual(
      res_watch.glob(['ConfigMap']),
      [{'kind': 'ConfigMap', 'name': 'master', 'status': 'positive', 'extras': {
        'foo': 'bar'
      }}]
    )


  def tearDown(self) -> None:
    super().tearDown()
    ns_factory.relinquish_all()