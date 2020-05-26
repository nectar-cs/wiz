from typing import Type

from wiz.model.base.wiz_model import WizModel
from wiz.model.operations.operation import Operation
from wiz.tests.models.test_wiz_model import Base


class TestOperation(Base.TestWizModel):

  @classmethod
  def model_class(cls) -> Type[WizModel]:
    return Operation
