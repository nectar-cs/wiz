import functools
from typing import Optional

from k8_kat.res.base.kat_res import KatRes
from wiz.core import tedi_client
from wiz.core.telem.ost import StepState
from wiz.model.base import res_selector
from wiz.model.base.wiz_model import WizModel

TOSS = Optional[StepState]


class Predicate(WizModel):

  def __init__(self, config):
    super().__init__(config)
    self.reason = None
    self.resources_considered = []

  def evaluate(self, step_state: TOSS = None) -> Optional[bool]:
    cond_type = self.config.get('type', 'resource-property-compare')
    if cond_type == 'resource-property-compare':
      return self.eval_resource_property()

    elif cond_type == 'resource-count-compare':
      return self.eval_resource_count()

    elif cond_type == 'chart-value-compare':
      return self.eval_resource_count()

    else:
      print("DANGER don't know condition type " + cond_type)
      return None

  def eval_resource_count(self) -> bool:
    selector_config = self.config.get('selector', '*:*')
    res_list = res_selector.res_sel_to_res(selector_config)
    check_against = self.config.get('check_against', 'positive')
    operator = self.config.get('op', 'equals')
    return comparator(operator)(len(res_list), check_against)

  def chart_value_compare(self):
    variable_name = self.config.get('variable')
    check_against = self.config.get('check_against')
    current_value = tedi_client.chart_value(variable_name)
    operator = self.config.get('op', 'equals')
    return comparator(operator)(current_value, check_against)

  def eval_resource_property(self) -> bool:
    prop_name = self.config.get('property', 'ternary_status')
    selector_config = self.config.get('selector', '*:*')
    match_type = self.config.get('match', 'all')
    check_against = self.config.get('check_against', 'positive')

    res_list = res_selector.res_sel_to_res(selector_config)
    self.resources_considered = list(map(KatRes.sig, res_list))

    operator = self.config.get('op', 'equals')
    compare_challenge = lambda v: comparator(operator)(v, check_against)
    prop_values = [getattr_deep(r, prop_name) for r in res_list]
    cond_met_evals = list(map(compare_challenge, prop_values))

    if match_type == 'all':
      return set(cond_met_evals) == {True}

    elif match_type == 'any':
      return True in cond_met_evals

    else:
      print("DANGER DONT KNOW MATCH TYPE" + match_type)
      return False


def getattr_deep(obj, attr):
  def _getattr(_obj, _attr):
    returned = getattr(_obj, _attr)
    return returned() if callable(returned) else returned
  try:
    return functools.reduce(_getattr, [obj] + attr.split('.'))
  except AttributeError:
    return None


def comparator(name):
  if name in ['equals', 'equal', 'eq', '==']:
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
    return lambda a, b: float(a) > float(b)
  elif name in ['lte', '<=']:
    return lambda a, b: float(a) <= float(b)
  elif name in ['is-defined']:
    return lambda a, b: bool(a)
  else:
    print("Don't know operator " + name)
    return lambda a, b: False
