from typing import Type

from nectwiz.model.base.wiz_model import WizModel, models_man
from nectwiz.model.predicate.common_predicates import TruePredicate, FalsePredicate
from nectwiz.model.predicate.multi_predicate import MultiPredicate
from nectwiz.tests.models.test_wiz_model import Base


class TestMultiPredicate(Base.TestWizModel):

  @classmethod
  def model_class(cls) -> Type[WizModel]:
    return MultiPredicate

  def test_multi_predicate_ands(self):
    models_man.clear(restore_defaults=True)
    predicate = MultiPredicate(dict(
      sub_predicates=[TruePredicate.__name__]
    ))
    self.assertTrue(predicate.evaluate())

    predicate = MultiPredicate(dict(
      sub_predicates=[
        TruePredicate.__name__,
        FalsePredicate.__name__
      ]
    ))
    self.assertFalse(predicate.evaluate())

    predicate = MultiPredicate(dict(
      sub_predicates=[
        TruePredicate.__name__,
        TruePredicate.__name__
      ]
    ))
    self.assertTrue(predicate.evaluate())

  def test_multi_predicate_ors(self):
    models_man.clear(restore_defaults=True)
    predicate = MultiPredicate(dict(
      operator='or',
      sub_predicates=[TruePredicate.__name__]
    ))
    self.assertTrue(predicate.evaluate())

    predicate = MultiPredicate(dict(
      operator='or',
      sub_predicates=[
        TruePredicate.__name__,
        FalsePredicate.__name__
      ]
    ))
    self.assertTrue(predicate.evaluate())

    predicate = MultiPredicate(dict(
      operator='or',
      sub_predicates=[
        TruePredicate.__name__,
        TruePredicate.__name__
      ]
    ))
    self.assertTrue(predicate.evaluate())

    predicate = MultiPredicate(dict(
      operator='or',
      sub_predicates=[
        FalsePredicate.__name__,
        FalsePredicate.__name__
      ]
    ))
    self.assertFalse(predicate.evaluate())
