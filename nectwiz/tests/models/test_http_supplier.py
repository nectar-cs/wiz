from typing import Type

from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.supply.http_data_supplier import HttpDataSupplier
from nectwiz.tests.models.test_wiz_model import Base
from nectwiz.tests.t_helpers import helper


class TestHttpSupplier(Base.TestWizModel):

  @classmethod
  def model_class(cls) -> Type[WizModel]:
    return HttpDataSupplier

  def test_produce(self):
    endpoint = f"{helper.ci_tams_name()}/1.0.0"
    instance = HttpDataSupplier(dict(endpoint=endpoint))
    print(instance._compute())
