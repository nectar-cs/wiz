from typing import Dict, Any, Optional

from werkzeug.utils import cached_property

from nectwiz.core.core import utils
from nectwiz.model.base.wiz_model import WizModel


class Predicate(WizModel):
  @cached_property
  def challenge(self):
    return self.get_prop('challenge')

  @cached_property
  def check_against(self) -> Optional[Any]:
    _value = self.get_prop('check_against')
    if _value is None:
      print(f"[nectwiz:predicate] check_against is undefined")
    return _value

  @cached_property
  def operator(self):
    return self.get_prop('operator', '==')

  @cached_property
  def tone(self):
    return self.get_prop('tone', 'error')

  @cached_property
  def reason(self):
    return self.get_prop('reason')

  def evaluate(self) -> bool:
    return self.perform_comparison(
      self.operator,
      self.challenge,
      self.check_against
    )

  # noinspection PyMethodMayBeStatic
  def error_extras(self) -> Dict:
    return {}

  # noinspection PyBroadException
  @staticmethod
  def perform_comparison(_name: str, challenge: Any, against: Any) -> bool:
    challenge = utils.unmuck_primitives(challenge)
    against = utils.unmuck_primitives(against)

    try:
      if _name in ['equals', 'equal', 'eq', '==', '=']:
        return challenge == against

      elif _name in ['not-equals', 'not-equal', 'neq', '!=', '=/=']:
        return not challenge == against

      elif _name in ['is-in', 'in']:
        return challenge in undefined_alias(against)

      elif _name in ['contains']:
        return against in undefined_alias(challenge)

      elif _name in ['only', 'contains-only']:
        return set(challenge) == {against}

      elif _name in ['is-greater-than', 'greater-than', 'gt', '>']:
        return challenge > against

      elif _name in ['gte', '>=']:
        return challenge >= against

      elif _name in ['is-less-than', 'less-than', 'lt', '<']:
        return challenge < against

      elif _name in ['lte', '<=']:
        return challenge <= against

      elif _name in ['presence', 'defined', 'is-defined']:
        return bool(challenge)

      elif _name in ['undefined', 'is-undefined']:
        return not challenge

      print(f"Don't know operator {_name}")
      return False
    except:
      return False


def undefined_alias(values):
  if type(values) == list:
    new_list = []
    for value in values or []:
      if not value:
        new_list.append('__undefined__')
      new_list.append(value)
    return new_list
  else:
    return values
