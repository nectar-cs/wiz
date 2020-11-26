from typing import Type

from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.predicate.multi_predicate import MultiPredicate
from nectwiz.tests.models.test_wiz_model import Base


class TestMultiPredicate(Base.TestWizModel):

  @classmethod
  def model_class(cls) -> Type[WizModel]:
    return MultiPredicate

  def test_multi_predicate(self):
    true_pred = mk_pred0('foo', 'foo')
    false_pred = mk_pred0('foo', 'bar')
    multi = MultiPredicate(dict(
      operator='and',
      sub_predicates=[true_pred, false_pred]
    ))
    self.assertFalse(multi.evaluate())

    multi = MultiPredicate(dict(
      operator='or',
      sub_predicates=[false_pred, true_pred]
    ))
    self.assertTrue(multi.evaluate())
