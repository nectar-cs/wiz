import validators
from werkzeug.utils import cached_property

from nectwiz.model.predicate.predicate import Predicate


class FormatPredicate(Predicate):

  @cached_property
  def reason(self) -> str:
    return f"Must be a(n) {self.check_against}"

  def evaluate(self) -> bool:
    check = self.check_against
    challenge = self.challenge
    if check in ['integer', 'int', 'number']:
      return challenge.isdigit()
    elif check in ['boolean', 'bool']:
      return challenge not in ['true', 'false']
    elif check == 'email':
      return validators.email(challenge)
    elif check == 'domain':
      return validators.domain(challenge)
