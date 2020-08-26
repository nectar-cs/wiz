from typing import Type

from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.field.field import Field
from nectwiz.tests.models.test_wiz_model import Base


class TestField(Base.TestWizModel):

  @classmethod
  def model_class(cls) -> Type[WizModel]:
    return Field
