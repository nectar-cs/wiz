from typing import Type

from nectwiz.core.core.types import ErrDict
from nectwiz.model.base.wiz_model import models_man, WizModel
from nectwiz.model.error import error_handler
from nectwiz.model.error.error_handler import ErrorHandler
from nectwiz.tests.models.test_wiz_model import Base


class TestErrorHandler(Base.TestWizModel):
  @classmethod
  def model_class(cls) -> Type[WizModel]:
    return ErrorHandler

  def test_find_handler_apply_err(self):
    models_man.clear(restore_defaults=True)
    handler = ErrorHandler.find_handler(dict(type='manifest_apply_failed'))
    self.assertIsNotNone(handler)
    self.assertEqual('nectar.error-handler.apply-failed', handler.id())

  def test_find_handler_await_failed(self):
    models_man.clear(restore_defaults=True)
    handler = ErrorHandler.find_handler(dict(type='res_settle_failed'))
    self.assertIsNotNone(handler)
    self.assertEqual('nectar.error-handler.await-failed', handler.id())

  def test_find_handler_general(self):
    models_man.clear(restore_defaults=False)
    models_man.add_descriptors(testing_error_handlers)
    handler = ErrorHandler.find_handler(dict(
      prop1='prop1-foo',
      prop2='prop2-foo'
    ))
    self.assertEqual('eh1', handler.id())

    handler = ErrorHandler.find_handler(dict(
      prop1='prop1-foo',
      prop2='prop2-baz'
    ))
    self.assertEqual('eh2', handler.id())

  def test_compute_diagnoses_ids(self):
    models_man.add_descriptors(testing_error_handlers)
    actual = ErrorHandler.compute_diagnoses_ids('eh1')
    self.assertEqual(['d11', 'd12'], actual)

    actual = ErrorHandler.compute_diagnoses_ids('eh2')
    self.assertEqual(['d22'], actual)


testing_error_handlers = [
  dict(
    id='eh1',
    kind=ErrorHandler.__name__,
    selector=dict(
      property_selector=dict(
        prop1=['prop1-foo', 'prop1-bar'],
        prop2=['prop2-foo'],
      )
    ),
    diagnoses=[
      dict(
        id='d11',
        predicate=dict(
          challenge='foo',
          check_against='foo'
        )
      ),
      dict(
        id='d12',
        predicate=dict(
          challenge='bar',
          check_against='bar'
        )
      )
    ]
  ),
  dict(
    id='eh2',
    kind=ErrorHandler.__name__,
    selector=dict(
      property_selector=dict(
        prop1=['prop1-foo', 'prop1-baz'],
        prop2=['prop2-baz'],
      )
    ),
    diagnoses=[
      dict(
        id='d21',
        predicate=dict(
          challenge='foo',
          check_against='baz'
        )
      ),
      dict(
        id='d22',
        predicate=dict(
          challenge='bar',
          check_against='bar'
        )
      )
    ]
  )
]
