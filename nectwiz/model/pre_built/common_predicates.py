from typing import Optional, Dict

import validators

from nectwiz.core.core import subs
from nectwiz.core.core.config_man import config_man
from nectwiz.model.base.resource_selector import ResourceSelector
from nectwiz.model.predicate.predicate import Predicate, getattr_deep


class ChartVarComparePredicate(Predicate):
  def __init__(self, config):
    super().__init__(config)
    self.variable_name = config.get('variable')

  def evaluate(self, context: Dict) -> bool:
    current_value = config_man.read_tam_var(self.variable_name)
    return self._common_compare(current_value)


class ResCountComparePredicate(Predicate):
  def __init__(self, config):
    super().__init__(config)
    self.selector_config = config.get('selector', '*:*')

  def evaluate(self, context: Dict) -> bool:
    res_list = self.selector().query_cluster(context)
    return self._common_compare(len(res_list))

  def selector(self) -> ResourceSelector:
    return ResourceSelector.inflate(self.selector_config)


class ResPropComparePredicate(Predicate):
  def __init__(self, config):
    super().__init__(config)
    self.selector_config = config.get('selector', '*:*')
    self.prop_name = config.get('property', 'ternary_status')
    self.match_type = config.get('match', 'all')

  def evaluate(self, context: Dict) -> bool:
    prop_name = subs.interp(self.prop_name, context)
    read_prop = lambda r: getattr_deep(r, prop_name)
    res_list = self.selector().query_cluster(context)
    resolved_values = list(map(read_prop, res_list))
    compare_challenge = lambda v: self._common_compare(v)
    cond_met_evals = list(map(compare_challenge, resolved_values))

    if self.match_type == 'all':
      return set(cond_met_evals) == {True}

    elif self.match_type == 'any':
      return True in cond_met_evals

    else:
      print("DANGER DONT KNOW MATCH TYPE" + self.match_type)
      return False

  def selector(self) -> ResourceSelector:
    expr = self.selector_config
    return ResourceSelector.inflate(expr)


class FormatPredicate(Predicate):

  def __init__(self, config: Dict):
    super().__init__(config)
    self.reason = f"Must be a(n) {self.check_against}"

  def evaluate(self, context: Dict) -> Optional[bool]:
    check = self.check_against
    challenge = context.get('value', self.challenge)
    if check == 'integer':
      return challenge.isdigit()
    elif check == 'boolean':
      return challenge not in ['true', 'false']
    elif check == 'email':
      return validators.email(challenge)
    elif check == 'domain':
      return validators.domain(challenge)
