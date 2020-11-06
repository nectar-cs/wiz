from typing import Dict, List

from nectwiz.core.core import subs
from nectwiz.core.core.types import KAOs, KAO
from nectwiz.model.base.resource_selector import ResourceSelector
from nectwiz.model.predicate.predicate import Predicate, getattr_deep


class ResourcePropertyPredicate(Predicate):
  def __init__(self, config):
    super().__init__(config)
    self.selector_config = config.get('selector')
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

  @classmethod
  def from_apply_outcome(cls, apply_outcomes: KAOs) -> Dict[str, List[Predicate]]:
    predicates = dict(positive=[], negative=[])
    for ktl_outcome in apply_outcomes:
      if not ktl_outcome['verb'] == 'unchanged':
        for charge in ['positive', 'negative']:
          predicate = cls.res_comp_predicate(ktl_outcome, charge)
          predicates[charge].append(predicate)
    return predicates

  @classmethod
  def res_comp_predicate(cls, ktl_out: KAO, charge):
    return cls(dict(
      id=f"{ktl_out['kind']}/{ktl_out['name']}-{charge}",
      title=f"{ktl_out['kind']}/{ktl_out['name']} is {charge}",
      property='ternary_status',
      check_against=charge,
      match_type='all',
      selector=dict(
        k8s_kind=ktl_out['kind'],
        name=ktl_out['name'],
        api_group=ktl_out['api_group']
      )
    ))
