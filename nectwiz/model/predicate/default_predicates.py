from typing import List, Dict

from nectwiz.core.core import utils
from nectwiz.model.pre_built.common_predicates import ResPropComparePredicate
from nectwiz.model.predicate.predicate import Predicate
from nectwiz.core.core.types import ApplyOutkome


def from_apply_outcome(apply_logs: List[str]) -> Dict[str, List[Predicate]]:
  predicates = dict(positive=[], negative=[])

  for log in apply_logs:
    ktl_outcome = utils.log2outkome(log)
    if ktl_outcome and not ktl_outcome['verb'] == 'unchanged':
      for charge in ['positive', 'negative']:
        predicate = res_comp_predicate(ktl_outcome, charge)
        predicates[charge].append(predicate)

  return predicates


def res_comp_predicate(ktl_out: ApplyOutkome, charge):
  return ResPropComparePredicate(dict(
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
