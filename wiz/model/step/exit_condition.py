from typing import Optional

from k8_kat.res.base.kat_res import KatRes
from wiz.core import step_job_client
from wiz.core.osr import StepState
from wiz.model.base import res_selector
from wiz.model.base.wiz_model import WizModel

TOSS = Optional[StepState]


class ExitCondition(WizModel):

  def __init__(self, config):
    super().__init__(config)
    self.reason = None
    self.resources_considered = []

  def evaluate(self, step_state: TOSS = None) -> Optional[bool]:
    cond_type = self.config.get('type', 'resource_property_compare')
    if cond_type == 'resource_property_compare':
      return self.eval_resource_property()

    else:
      print("DANGER don't know condition type " + cond_type)
      return None

  def comparator(self):
    name = self.config.get('op', 'equals')
    if name in ['equals', 'equal', 'eq', '==']:
      return lambda a, b: str(a) == str(b)
    elif name in ['not-equals', 'not-equal', 'neq', '!=']:
      print("BOOP")
      return lambda a, b: str(a) != str(b)
    else:
      print("Don't know operator " + name)
      return lambda a, b: False

  def eval_resource_property(self) -> bool:
    prop_name = self.config.get('property', 'ternary_status')
    selector_config = self.config.get('selector', '*:*')
    match_type = self.config.get('match', 'all')
    check_against = self.config.get('check_against', 'positive')

    res_list = res_selector.res_sel_to_res(selector_config)
    self.resources_considered = list(map(KatRes.sig, res_list))

    compare_challenge = lambda v: self.comparator()(v, check_against)
    read_prop = lambda x: x() if callable(x) else x
    prop_values = [read_prop(getattr(r, prop_name)) for r in res_list]
    cond_met_evals = list(map(compare_challenge, prop_values))

    if match_type == 'all':
      return set(cond_met_evals) == {True}

    elif match_type == 'any':
      return True in cond_met_evals

    else:
      print("DANGER DONT KNOW MATCH TYPE" + match_type)
      return False
