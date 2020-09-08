from typing import List, Dict

from nectwiz.core.core import utils
from nectwiz.model.pre_built.common_predicates import ResPropComparePredicate
from nectwiz.model.predicate.predicate import Predicate


def from_apply_outcome(apply_logs: List[str]) -> Dict[str, List[Predicate]]:
  predicates = dict(positive=[], negative=[])

  for log in apply_logs:
    ktl_outcome = utils.log2ktlapplyoutcome(log)
    if ktl_outcome['verb'] is not 'unchanged':
      for charge in ['positive', 'negative']:
        predicate = res_comp_predicate(ktl_outcome, charge)
        predicates[charge].append(predicate)

  return predicates


def res_comp_predicate(ktl_outcome, charge):
  return ResPropComparePredicate(dict(
    title=f"Changed resources have a {charge} status",
    property='ternary_status',
    check_against=charge,
    match_type='all',
    selector=f"{ktl_outcome['kind']}:{ktl_outcome['name']}"
  ))
