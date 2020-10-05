from typing import List, Dict

from nectwiz.model.pre_built.common_predicates import ResourcePropertyPredicate
from nectwiz.model.predicate.predicate import Predicate
from nectwiz.core.core.types import KAO, KAOs


def from_apply_outcome(apply_outcomes: KAOs) -> Dict[str, List[Predicate]]:
  predicates = dict(positive=[], negative=[])
  for ktl_outcome in apply_outcomes:
    if not ktl_outcome['verb'] == 'unchanged':
      for charge in ['positive', 'negative']:
        predicate = res_comp_predicate(ktl_outcome, charge)
        predicates[charge].append(predicate)
  return predicates


def res_comp_predicate(ktl_out: KAO, charge):
  return ResourcePropertyPredicate(dict(
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
