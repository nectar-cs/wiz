import time
from typing import Type

from k8kat.utils.testing import simple_pod, ns_factory

from nectwiz.core.core.config_man import config_man
from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.supply.resources_supplier import ResourcesSupplier
from nectwiz.tests.models.test_wiz_model import Base
from nectwiz.tests.t_helpers.helper import create_base_master_map


class TestResourcesSupplier(Base.TestWizModel):

  @classmethod
  def model_class(cls) -> Type[WizModel]:
    return ResourcesSupplier

  def test_produce_dict(self):
    config_man._ns, = ns_factory.request(1)
    create_base_master_map(config_man.ns())
    simple_pod.create(name='p1', ns=config_man.ns())
    simple_pod.create(name='p2', ns=config_man.ns())

    inst = ResourcesSupplier(dict(
      output='options_format',
      selector='Pod:*',
      many=False
    ))

    result = inst.resolve()
    self.assertEqual({'id': 'p1', 'title': 'p1'},  result)

  def test_produce_str(self):
    config_man._ns, = ns_factory.request(1)
    create_base_master_map(config_man.ns())
    simple_pod.create(name='p1', ns=config_man.ns())

    inst = ResourcesSupplier(dict(
      output='raw.status.phase',
      selector='Pod:*',
      many=True
    ))

    result = inst.resolve()
    self.assertEqual(["Pending"], result)
