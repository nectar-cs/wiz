from typing import Dict

from nectwiz.model.predicate.predicate import Predicate


class MultiPredicate(Predicate):
  def __init__(self, config: Dict):
    super().__init__(config)
    self.operator = self.get_prop('operator', 'and')

  def evaluate(self) -> bool:
    sub_preds = self.inflate_children('sub_predicates', Predicate)
    for sub_pred in sub_preds:
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
    if self.operator == 'or':
      return False
    elif self.operator == 'and':
      return True
    else:
      print(f"[nectwiz::multipredicate] illegal operator {self.operator}")
      return False
