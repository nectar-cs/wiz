from typing import Type

from wiz.model.base.wiz_model import WizModel
from wiz.model.field.field import Field
from wiz.tests.models.test_wiz_model import Base


class TestField(Base.TestWizModel):

  @classmethod
  def model_class(cls) -> Type[WizModel]:
    return Field
