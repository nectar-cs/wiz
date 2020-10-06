from nectwiz.model.base.wiz_model import models_man
from nectwiz.tests.t_helpers.cluster_test import ClusterTest


class TestUpdateAction(ClusterTest):

  def setUp(self) -> None:
    models_man.clear(restore_defaults=True)

  # def test_e2e(self):
  #   config_man._ns, = ns_factory.request(1)
  #   create_base_master_map(config_man.ns())
  #
  #   config_man.write_tam(TamDict(
  #     version='1.0.0',
  #     type='image',
  #     uri=ci_tami_name(),
  #     args=None
  #   ))
  #
  #   telem_man.clear_update_outcomes()
  #   updates_man.install_update(update_package)
  #   telem_man.list_update_outcomes()
  #   outcome = telem_man.get_update_outcome('foo')
  #   self.assertIsNotNone(outcome)
  #   self.assertEqual('1.0.0', outcome['version_pre'])
  #   self.assertEqual('positive', outcome['status'])
