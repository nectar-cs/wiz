from typing import Type

from nectwiz.model.base.wiz_model import WizModel, models_man
from nectwiz.model.field.field import Field
from nectwiz.tests.models.test_wiz_model import Base


class TestField(Base.TestWizModel):

  @classmethod
  def model_class(cls) -> Type[WizModel]:
    return Field

  def test_delegate_explicit(self):

    models_man.add_descriptors([
      dict(
        kind='GenericVariable',

      )
    ])

    Field(dict(

    ))
