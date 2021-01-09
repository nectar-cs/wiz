from typing import Type

from k8kat.utils.testing import ns_factory

from nectwiz.core.core import consts
from nectwiz.core.core.config_man import config_man
from nectwiz.model.action.actions.apply_manifest_action import ApplyManifestAction
from nectwiz.model.base.wiz_model import WizModel, models_man
from nectwiz.tests.models.test_wiz_model import Base
from nectwiz.tests.t_helpers import helper
from nectwiz.tests.t_helpers.helper import create_base_master_map

subj = ApplyManifestAction

class TestApplyManifestAction(Base.TestWizModel):

  @classmethod
  def model_class(cls) -> Type[WizModel]:
    return ApplyManifestAction

  def test_perform(self):
    config_man._ns, = ns_factory.request(1)
    models_man.clear(restore_defaults=True)
    create_base_master_map(config_man.ns())
    config_man.patch_manifest_vars({'k': 3})

    action = ApplyManifestAction(dict(
      tam={
        'type': consts.virtual_tam,
        'uri': helper.TrivialVirtualTam
      }
    ))

    action.perform()
    progress = action.observer.progress
    sub_statuses = [s['status'] for s in progress['sub_items']]
    self.assertEqual("positive", progress['status'])
    self.assertEqual({'positive'}, set(sub_statuses))

  def test_compute_values_vanilla(self):
    config_man._ns, = ns_factory.request(1)
    models_man.clear(restore_defaults=True)
    create_base_master_map(config_man.ns())

    config_man.patch_manifest_defaults({'foo': 'bar', 'bar': 'baz'})
    config_man.patch_manifest_vars({'foo': 'oof'})

    result = subj({}).compute_values()
    self.assertEqual({'foo': 'oof', 'bar': 'baz'}, result)

  def test_compute_values_with_literals(self):
    action = subj({subj.KEY_VALUES: {'foo': 'bu'}})
    self.assertEqual({'foo': 'bu'}, action.compute_values())

    action = subj({subj.KEY_VALUES: [{'foo': 'bu'}]})
    self.assertEqual({'foo': 'bu'}, action.compute_values())
