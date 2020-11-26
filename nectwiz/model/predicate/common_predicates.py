from nectwiz.model.predicate.predicate import Predicate


class TruePredicate(Predicate):
  def evaluate(self) -> bool:
    return True


class FalsePredicate(Predicate):
  def evaluate(self) -> bool:
    return False
