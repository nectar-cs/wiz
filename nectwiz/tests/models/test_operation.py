from typing import Type

from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.operations.operation import Operation
from nectwiz.tests.models.test_wiz_model import Base


class TestOperation(Base.TestWizModel):

  @classmethod
  def model_class(cls) -> Type[WizModel]:
    return Operation
