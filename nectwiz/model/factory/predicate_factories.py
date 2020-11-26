from typing import Dict, List

from nectwiz.core.core.types import KAO, KAOs
from nectwiz.model.predicate.predicate import Predicate


class PredicateFactory:

  @staticmethod
  def from_apply_outcome(apply_outcomes: KAOs) -> Dict[str, List[Predicate]]:
    predicates = dict(positive=[], negative=[])
    for ktl_outcome in apply_outcomes:
      if not ktl_outcome['verb'] == 'unchanged':
        for charge in ['positive', 'negative']:
          predicate = PredicateFactory.res_comp_predicate(ktl_outcome, charge)
          predicates[charge].append(predicate)
    return predicates

  @staticmethod
  def res_comp_predicate(ktl_out: KAO, charge):
    from nectwiz.model.supply.resources_supplier import ResourcesSupplier
    return Predicate(dict(
      id=f"{ktl_out['kind']}/{ktl_out['name']}-{charge}",
      title=f"{ktl_out['kind']}/{ktl_out['name']} is {charge}",
      check_against=charge,
      operator='only',
      challenge=dict(
        kind=ResourcesSupplier.__name__,
        output='ternary_status',
        many=True,
        selector=dict(
          k8s_kind=ktl_out['kind'],
          name=ktl_out['name'],
          api_group=ktl_out['api_group']
        )
      )
    ))
