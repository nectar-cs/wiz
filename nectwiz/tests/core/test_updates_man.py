import time

from k8kat.res.pod.kat_pod import KatPod
from k8kat.utils.testing import ns_factory

from nectwiz.core.core.config_man import config_man
from nectwiz.core.core.types import TamDict, UpdateDict
from nectwiz.core.telem import updates_man
from nectwiz.model.base.wiz_model import models_man
from nectwiz.tests.t_helpers.cluster_test import ClusterTest
from nectwiz.tests.t_helpers.helper import ci_tami_name, create_base_master_map


class TestUpdatesMan(ClusterTest):

  def test_apply_release_update(self):
    config_man._ns, = ns_factory.request(1)
    create_base_master_map(config_man.ns())

    config_man.write_tam(TamDict(
      ver='1.0.0',
      type='image',
      uri=ci_tami_name(),
      args=None
    ))

    config_man.commit_keyed_mfst_vars([
      ('pod.name', 'legally-custom'),
    ])

    models_man.add_descriptors([
      dict(
        kind='ChartVariable',
        id='pod.image',
        release_overridable=True
      ),
      dict(
        kind='ChartVariable',
        id='pod.name',
        release_overridable=False
      )
    ])

    update_package = UpdateDict(
      id='foo',
      type='release',
      version='2.0.0',
      injections={}
    )

    updates_man.apply_upgrade(update_package)
    time.sleep(4)

    ns, defs = config_man.ns(), config_man.tam_defaults(True)
    tam, mfst_vars = config_man.tam(True), config_man.mfst_vars(True)
    self.assertEqual("2.0.0", tam.get('ver'))
    self.assertEqual(ci_tami_name(), tam.get('uri'))

    self.assertEqual('nginx:1.19.2', mfst_vars['pod']['image'])
    self.assertEqual('legally-custom', mfst_vars['pod']['name'])

    self.assertEqual('nginx:1.19.2', defs['pod']['image'])
    self.assertEqual('pod', defs['pod']['name'])

    self.assertIsNotNone(KatPod.find('legally-custom', ns))