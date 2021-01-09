from typing import Dict, List

from k8kat.utils.testing import ns_factory

from nectwiz.core.core import updates_man, consts
from nectwiz.core.core.config_man import config_man
from nectwiz.core.tam.virtual_tam_client import VirtualTamClient
from nectwiz.model.base.wiz_model import models_man
from nectwiz.model.variable.manifest_variable import ManifestVariable
from nectwiz.tests.t_helpers.cluster_test import ClusterTest
from nectwiz.tests.t_helpers.helper import create_base_master_map


class TestUpdatesMan(ClusterTest):
  def test_preview(self):
    update = dict(
      version='1',
      tam_type=consts.virtual_tam,
      tam_uri=VirtualTamV2
    )
    updates_man.preview(update)

  def test_compute_new_manifest_vars(self):
    config_man._ns, = ns_factory.request(1)

    create_base_master_map(config_man._ns)

    config_man.patch_manifest_vars(dict(
      ingress=dict(on=True),
      dep=dict(v=1)
    ))

    models_man.add_descriptors([
      {
        'kind': ManifestVariable.kind(),
        'id': 'dep.v',
        ManifestVariable.RELEASE_OVERRIDE_KEY: True
      }
    ])

    exp = dict(ingress=dict(on=True), dep=(dict(v=2)))
    result = updates_man.compute_new_manifest_vars(dict(
      ingress=dict(on=False),
      dep=(dict(v=2))
    ))

    self.assertEqual(exp, result)


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
