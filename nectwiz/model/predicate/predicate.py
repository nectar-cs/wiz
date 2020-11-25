from typing import Callable, Dict, Any

from nectwiz.core.core import subs, utils
from nectwiz.model.base.wiz_model import WizModel


class Predicate(WizModel):
  def __init__(self, config: Dict):
    super().__init__(config)
    self.reason: str = config.get('reason')
    self.tone: str = config.get('tone', 'error')
    self.operator: str = config.get('operator', 'equals')
    self.challenge: Any = config.get('challenge')
    self.check_against: Any = config.get('check_against')

  def evaluate(self, context: Dict) -> bool:
    fresher_challenge = (context or {}).get('value')
    challenge = fresher_challenge or self.challenge
    challenge = subs.interp(challenge, context)
    return self._common_compare(challenge)

  def _common_compare(self, value) -> bool:
    challenge = utils.unmuck_primitives(value)
    against = utils.unmuck_primitives(self.check_against)
    comparator = build_comparator(self.operator)
    return comparator(challenge, against)

  # noinspection PyMethodMayBeStatic
  def error_extras(self) -> Dict:
    return {}

def build_comparator(name) -> Callable[[any, any], bool]:
  """
  Map of operations to all the possible ways they can be named by the vendor.
  :param name: vendor-defined operator name.
  :return: actual operation to be performed.
  """

  def false_on_raise(actual_pred: Callable):
    try:
      return actual_pred()
    except:
      return False

  if name in ['equals', 'equal', 'eq', '==', '=']:
    return lambda a, b: a == b
  elif name in ['not-equals', 'not-equal', 'neq', '!=', '=/=']:
    return lambda a, b: a != b
  elif name in ['is-in', 'in']:
    return lambda a, b: false_on_raise(lambda: a in undefined_alias(b))
  elif name in ['contains']:
    return lambda a, b: false_on_raise(lambda: b in a)
  elif name in ['is-greater-than', 'greater-than', 'gt', '>']:
    return lambda a, b: false_on_raise(lambda: a > float(b))
  elif name in ['gte', '>=']:
    return lambda a, b: false_on_raise(lambda: float(a) >= float(b))
  elif name in ['is-less-than', 'less-than', 'lt', '<']:
    return lambda a, b: false_on_raise(lambda: float(a) < float(b))
  elif name in ['lte', '<=']:
    return lambda a, b: false_on_raise(lambda: float(a) <= float(b))
  elif name in ['presence', 'defined', 'is-defined']:
    return lambda a, b: bool(a)
  elif name in ['undefined', 'is-undefined']:
    return lambda a, b: not bool(a)
  else:
    print(f"Don't know operator {name}")
    return lambda a, b: False


def undefined_alias(values):
  pimped = []
  for value in values or []:
    if not value or value == '':
      pimped.append('__undefined__')
    pimped.append(value)
  return pimped
