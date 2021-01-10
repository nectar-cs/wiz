from typing import Dict, List

from k8kat.utils.testing import ns_factory

from nectwiz.core.core import updates_man, consts
from nectwiz.core.core.config_man import config_man
from nectwiz.core.tam.virtual_tam_client import VirtualTamClient
from nectwiz.tests.t_helpers.cluster_test import ClusterTest
from nectwiz.tests.t_helpers.helper import create_base_master_map


class TestUpdatesMan(ClusterTest):

  def test_commit_new_tam(self):
    config_man._ns, = ns_factory.request(1)
    create_base_master_map(config_man._ns)

  def test_preview(self):
    config_man._ns, = ns_factory.request(1)
    create_base_master_map(config_man._ns)

    update = dict(
      version='1',
      tam_type=consts.virtual_tam,
      tam_uri=VirtualTamV2
    )

    config_man.patch_manifest_defaults(dict(
      ingress=dict(on=False),
      dep=dict(v=1)
    ))

    config_man.patch_manifest_vars(dict(
      ingress=dict(on=False),
      dep=dict(v=1)
    ))

    updates_man.preview(update)


class VirtualTamV1(VirtualTamClient):
  def _template(self, values: Dict) -> List[Dict]:
    return [
      dict(ingress=dict(on=values['ingress']['on'])),
      dict(dep=dict(v=values['dep']['v'])),
    ]

  def _default_values(self) -> Dict:
    return dict(ingress=dict(on=False), dep=dict(v=1))


class VirtualTamV2(VirtualTamV1):
  def _default_values(self) -> Dict:
    return {
      **super()._default_values(),
      'dep': {'v': 2}
    }
