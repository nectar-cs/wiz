from nectwiz.core.core import config_man
from nectwiz.model.base import res_selector
from nectwiz.model.predicate.predicate import Predicate, getattr_deep


class ChartVarComparePredicate(Predicate):
  def __init__(self, config):
    super().__init__(config)
    self.variable_name = config.get('variable')

  def evaluate(self) -> bool:
    current_value = config_man.read_tam_var(self.variable_name)
    return self._common_compare(current_value)


class ResCountComparePredicate(Predicate):
  def __init__(self, config):
    super().__init__(config)
    self.selector_config = config.get('selector', '*:*')

  def evaluate(self) -> bool:
    res_list = res_selector.to_reslist(self.selector_config)
    return self._common_compare(len(res_list))


class ResPropComparePredicate(Predicate):
  def __init__(self, config):
    super().__init__(config)
    self.selector_config = config.get('selector', '*:*')
    self.prop_name = config.get('property', 'ternary_status')
    self.match_type = config.get('match', 'all')

  def evaluate(self) -> bool:
    res_list = res_selector.to_reslist(self.selector_config)

    resolved_values = [getattr_deep(r, self.prop_name) for r in res_list]
    compare_challenge = lambda v: self._common_compare(v)
    cond_met_evals = list(map(compare_challenge, resolved_values))

    if self.match_type == 'all':
      return set(cond_met_evals) == {True}

    elif self.match_type == 'any':
      return True in cond_met_evals

    else:
      print("DANGER DONT KNOW MATCH TYPE" + self.match_type)
      return False
