from typing import List

from nectwiz.core.core import utils
from nectwiz.model.pre_built.common_predicates import ResPropComparePredicate
from nectwiz.model.predicate.predicate import Predicate


def from_apply_outcome(apply_logs: List[str]) -> List[Predicate]:
  predicates = []
  for log in apply_logs:
    ktl_outcome = utils.log2ktlapplyoutcome(log)
    if ktl_outcome['verb'] is not 'unchanged':
      predicates.append(ResPropComparePredicate(dict(
        property='ternary_status',
        match_type='all',
        selector=f"{ktl_outcome['kind']}:{ktl_outcome['name']}"
      )))
  return predicates

