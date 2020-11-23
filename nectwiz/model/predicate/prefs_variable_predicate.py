from typing import Dict

from nectwiz.core.core.config_man import config_man
from nectwiz.model.predicate.predicate import Predicate


class PrefsVariablePredicate(Predicate):
  def __init__(self, config):
    super().__init__(config)
    self.variable_name = config.get('variable')

  def evaluate(self, context: Dict) -> bool:
    current_value = config_man.pref_var(self.variable_name)
    return self._common_compare(current_value)
