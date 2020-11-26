from typing import List

from werkzeug.utils import cached_property

from nectwiz.model.predicate.predicate import Predicate


class MultiPredicate(Predicate):

  SUB_PREDICATES_KEY = 'sub_predicates'

  @cached_property
  def sub_predicates(self) -> List[Predicate]:
    return self.inflate_children(
      Predicate,
      prop=self.SUB_PREDICATES_KEY
    )

  @cached_property
  def operator(self):
    return self.get_prop(self.OPERATOR_KEY, 'and')

  def evaluate(self) -> bool:
    if len(self.sub_predicates) == 0:
      return self.operator == 'or'

    for sub_pred in self.sub_predicates:
      evaluated_to_true = sub_pred.evaluate()
      if self.operator == 'or':
        if evaluated_to_true:
          return True
      elif self.operator == 'and':
        if not evaluated_to_true:
          return False
      else:
        print(f"[nectwiz::multipredicate] illegal operator {self.operator}")
        return False
    return self.operator == 'and'
