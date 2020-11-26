from typing import Type

from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.operation.field import Field
from nectwiz.tests.models.test_wiz_model import Base


class TestField(Base.TestWizModel):

  @classmethod
  def model_class(cls) -> Type[WizModel]:
    return Field

  def test_delegate_inside(self):
    field = Field(dict(
      id='bar',
      title='t',
      info='i'
    ))
    self.assertEqual('bar', field.id())
    self.assertEqual('t', field.title)
    self.assertEqual('i', field.info)

  def test_delegate_outside(self):
    field = Field(dict(
      id='foo',
      variable=dict(
        title='generic-t',
        info='generic-i'
      )
    ))

    self.assertEqual('generic-t', field.title)
    self.assertEqual('generic-i', field.info)
