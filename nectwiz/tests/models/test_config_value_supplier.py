from typing import Type

from k8kat.utils.testing import ns_factory

from nectwiz.core.core.config_man import config_man, tam_vars_key, prefs_config_key
from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.supply.config_value_supplier import ConfigValueSupplier
from nectwiz.tests.models.test_wiz_model import Base
from nectwiz.tests.t_helpers.helper import create_base_master_map

subj = ConfigValueSupplier

class TestConfigValueSupplier(Base.TestWizModel):

  @classmethod
  def model_class(cls) -> Type[WizModel]:
    return ConfigValueSupplier

  def test_resolve(self):
    config_man._ns, = ns_factory.request(1)
    create_base_master_map(config_man.ns())
    config_man.patch_manifest_vars(dict(foo='bar'))
    config_man.patch_prefs(dict(bar=dict(bor='at')))

    supplier1 = subj({
      subj.OUTPUT_FMT_KEY: 'foo',
      subj.KEY_FIELD_KEY: tam_vars_key
    })

    supplier2 = subj({
      subj.OUTPUT_FMT_KEY: 'bar',
      subj.KEY_FIELD_KEY: 'an-nonexistent-key'
    })

    supplier3 = subj({
      subj.OUTPUT_FMT_KEY: 'bar',
      subj.KEY_FIELD_KEY: prefs_config_key
    })

    self.assertEqual('bar', supplier1.resolve())
    self.assertEqual(None, supplier2.resolve())
    self.assertEqual(dict(bor='at'), supplier3.resolve())
