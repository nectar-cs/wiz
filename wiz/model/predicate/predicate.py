import functools
from typing import Optional, Callable

from k8_kat.res.base.kat_res import KatRes
from wiz.core import tami_client
from wiz.core.telem.ost import StepState
from wiz.model.base import res_selector
from wiz.model.base.wiz_model import WizModel

TOSS = Optional[StepState]


class Predicate(WizModel):

  def __init__(self, config):
    super().__init__(config)
    self.reason = None
    self.resources_considered = []

  @property
  def tone(self) -> str:
    """
    Getter for tone of the evaluation. Default is "error".
    :return: tone of evaluation, in string form.
    """
    return self.config.get('tone', 'error')

  def evaluate(self, step_state: TOSS = None) -> Optional[bool]:
    """
    Chooses the appropriate evaluation procedure based on condition type
    and performs it.
    :param step_state: necessary for implementation by vendors.
    :return: the result of evaluation - True if success, False otherwise.
    """
    cond_type = self.config.get('type', 'resource-property-compare')
    if cond_type == 'resource-property-compare':
      return self.eval_resource_property()

    elif cond_type == 'resource-count-compare':
      return self.eval_resource_count()

    elif cond_type == 'chart-value-compare':
      return self.chart_value_compare()

    else:
      print("DANGER don't know condition type " + cond_type)
      return None

  def eval_resource_count(self) -> bool:
    """
    Evaluates if the resource matches up with the desired value.
    :return: True if matches up, False otherwise.
    """
    selector_config = self.config.get('selector', '*:*')
    res_list = res_selector.res_sel_to_res(selector_config)
    check_against = self.config.get('check_against')
    operator = self.config.get('op', 'equals')
    return comparator(operator)(len(res_list), check_against)

  def chart_value_compare(self) -> bool:
    """
    Evaluates if a given chart variable matches up with the desired value.
    :return: True if matches up, False otherwise.
    """
    variable_name = self.config.get('variable')
    check_against = self.config.get('check_against')
    current_value = tami_client.chart_value(variable_name)
    operator = self.config.get('op', 'equals')
    return comparator(operator)(current_value, check_against)

  def eval_resource_property(self) -> bool:
    """
    Evaluates a certain attribute for all eligible KatRes resources. Occurs in
    3 steps:
      1. Locate the eligible resource set based on Predicate's selector
      2. Evaluate the chosen attribute for each of the eligible resoruces
      3. Depending on match type (all or any) output a boolean to describe
      evaluation success or failure
    :return: True if evaluation succeeds, False otherwise.
    """
    # Step 1
    selector_config = self.config.get('selector', '*:*')
    res_list = res_selector.res_sel_to_res(selector_config)
    self.resources_considered = list(map(KatRes.sig, res_list))

    # Step 2
    prop_name = self.config.get('property', 'ternary_status')
    prop_values = [getattr_deep(r, prop_name) for r in res_list]
    operator = self.config.get('op', 'equals')
    check_against = self.config.get('check_against', 'positive')
    compare_challenge = lambda v: comparator(operator)(v, check_against)
    cond_met_evals = list(map(compare_challenge, prop_values))

    # Step 3
    match_type = self.config.get('match', 'all')
    if match_type == 'all':
      return set(cond_met_evals) == {True}

    elif match_type == 'any':
      return True in cond_met_evals

    else:
      print("DANGER DONT KNOW MATCH TYPE" + match_type)
      return False


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
