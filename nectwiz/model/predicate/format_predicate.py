from typing import Dict

import validators

from nectwiz.model.predicate.predicate import Predicate


class FormatPredicate(Predicate):

  def __init__(self, config: Dict):
    super().__init__(config)
    self.reason = f"Must be a(n) {self.check_against}"

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

