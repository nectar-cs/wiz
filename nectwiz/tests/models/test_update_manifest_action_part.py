from k8kat.utils.testing import ns_factory

from nectwiz.core.core.config_man import config_man
from nectwiz.core.core.types import TamDict
from nectwiz.model.action.action_parts.update_manifest_defaults_action_part import UpdateManifestDefaultsActionPart
from nectwiz.model.action.base.observer import Observer
from nectwiz.model.base.wiz_model import models_man
from nectwiz.model.variable.manifest_variable import ManifestVariable
from nectwiz.tests.t_helpers.cluster_test import ClusterTest
from nectwiz.tests.t_helpers.helper import ci_tami_name, create_base_master_map


class TestUpdateManifestDefaultsActionPart(ClusterTest):

  def setUp(self) -> None:
    models_man.clear(restore_defaults=True)

  def test_apply_release_update(self):
    config_man._ns, = ns_factory.request(1)
    create_base_master_map(config_man.ns())

    config_man.write_tam(TamDict(
      version='1.0.0',
      type='image',
      uri=ci_tami_name(),
      args=None
    ))

    config_man.patch_keyed_manifest_vars([
      ('pod.name', 'legally-custom'),
    ])

    models_man.add_descriptors([
      dict(
        kind=ManifestVariable.__name__,
        id='pod.image',
        release_overridable=True
      ),
      dict(
        kind=ManifestVariable.__name__,
        id='pod.name',
        release_overridable=False
      )
    ])

    UpdateManifestDefaultsActionPart.perform(Observer(), update_package)

    tam = config_man.tam(reload=True)
    manifest_defaults = config_man.manifest_defaults(True)
    manifest_variables = config_man.manifest_vars(True)

    self.assertEqual("2.0.0", tam.get('version'))
    self.assertEqual(ci_tami_name(), tam.get('uri'))

    self.assertEqual('nginx:1.19.2', manifest_variables['pod']['image'])
    self.assertEqual('legally-custom', manifest_variables['pod']['name'])

    self.assertEqual('nginx:1.19.2', manifest_defaults['pod']['image'])
    self.assertEqual('pod', manifest_defaults['pod']['name'])


update_package = dict(
  id='foo',
  type='release',
  version='2.0.0',
  injections={},
  manual=False,
  tam_type=None,
  tam_uri=None,
  note='irrelevant'
)
