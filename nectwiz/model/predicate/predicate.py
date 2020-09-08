import functools
from typing import Optional, Callable

from nectwiz.model.base.wiz_model import WizModel


class Predicate(WizModel):

  def __init__(self, config):
    super().__init__(config)
    self.reason = None
    self.tone = config.get('tone', 'error')
    self.operator = config.get('op', 'equals')
    self.check_against = config.get('check_against')

  def evaluate(self) -> Optional[bool]:
    raise NotImplemented

  def _common_compare(self, value):
    return comparator(self.operator)(value, self.check_against)


def getattr_deep(obj, attr):
  """
  Deep attribute getter.
  :param obj: Object from which to get the attribute.
  :param attr: attribute to get.
  :return: value of the attribute if found, else None.
  """
  def _getattr(_obj, _attr):
    returned = getattr(_obj, _attr)
    return returned() if callable(returned) else returned
  try:
    return functools.reduce(_getattr, [obj] + attr.split('.'))
  except AttributeError:
    return None


def comparator(name) -> Callable[[any, any], bool]:
  """
  Map of operations to all the possible ways they can be named by the vendor.
  :param name: vendor-defined operator name.
  :return: actual operation to be performed.
  """
  if name in ['equals', 'equal', 'eq', '==', '=']:
    return lambda a, b: str(a) == str(b)
  elif name in ['not-equals', 'not-equal', 'neq', '!=']:
    return lambda a, b: str(a) != str(b)
  elif name in ['is-in', 'in']:
    return lambda a, b: a in b
  elif name in ['is-greater-than', 'greater-than', 'gt', '>']:
    return lambda a, b: float(a) > float(b)
  elif name in ['gte', '>=']:
    return lambda a, b: float(a) >= float(b)
  elif name in ['is-less-than', 'less-than', 'lt', '<']:
    return lambda a, b: float(a) < float(b)
  elif name in ['lte', '<=']:
    return lambda a, b: float(a) <= float(b)
  elif name in ['defined', 'is-defined']:
    return lambda a, b: bool(a)
  elif name in ['undefined', 'is-undefined']:
    return lambda a, b: not bool(a)
  else:
    print(f"Don't know operator {name}")
    return lambda a, b: False
