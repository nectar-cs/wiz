from typing import Type

from nectwiz.model.input.input import GenericInput

from nectwiz.model.base.wiz_model import WizModel, models_man
from nectwiz.model.field.field import Field
from nectwiz.tests.models.test_wiz_model import Base


class TestField(Base.TestWizModel):

  @classmethod
  def model_class(cls) -> Type[WizModel]:
    return Field

  def test_default_input_spec(self):
    spec = Field({}).input_spec()
    self.assertEqual(GenericInput, spec.__class__)

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
    models_man.add_descriptors([
      dict(
        id='foo',
        kind='GenericVariable',
        title='generic-t',
        info='generic-i'
      )
    ])

    field = Field(dict(id='foo', variable_id='foo'))
    self.assertEqual('foo', field.id())
    self.assertEqual('generic-t', field.title)
    self.assertEqual('generic-i', field.info)
