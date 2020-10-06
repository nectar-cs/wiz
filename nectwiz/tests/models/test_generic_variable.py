from typing import Type

from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.variable.generic_variable import GenericVariable
from nectwiz.tests.models.test_wiz_model import Base


class TestGenericVariable(Base.TestWizModel):

  @classmethod
  def model_class(cls) -> Type[WizModel]:
    return GenericVariable

  def test_validate_when_valid(self):
    gv = GenericVariable(dict(
      validation=[
        dict(
          id='eq-foo',
          type='eq',
          check_against='foo'
        )
      ]
    ))
    actual = gv.validate('foo', {})
    self.assertTrue(actual['met'])

  def test_validate_when_not_valid(self):
    gv = GenericVariable(dict(
      validation=[
        dict(
          id='eq-foo',
          type='eq',
          check_against='foo'
        ),
        dict(
          id='eq-bar',
          type='eq',
          check_against='bar',
          tone='warning',
          reason='because'
        )
      ]
    ))

    actual = gv.validate('foo', {})
    self.assertFalse(actual['met'])
    self.assertEqual('warning', actual['tone'])
    self.assertEqual('because', actual['reason'])
