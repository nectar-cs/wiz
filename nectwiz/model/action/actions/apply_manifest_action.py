from typing import List, Dict, Union

from werkzeug.utils import cached_property

from nectwiz.core.core.config_man import config_man
from nectwiz.core.core.types import TamDict, ProgressItem, KoD
from nectwiz.core.core.utils import deep_merge
from nectwiz.model.action.action_parts.apply_manifest_action_part \
  import ApplyManifestActionPart
from nectwiz.model.action.action_parts.await_predicates_settle_action_part \
  import AwaitPredicatesSettleActionPart
from nectwiz.model.action.base.action import Action
from nectwiz.model.base.resource_selector import ResourceSelector
from nectwiz.model.factory.predicate_factories import PredicateFactory


class ApplyManifestAction(Action):
  KEY_APPLY_FILTERS = 'apply_filters'
  KEY_TAM = 'tam'
  KEY_VALUES = 'values'
  KEY_IN_MEMORY_VALUES = 'in_memory_values'

  DEFAULT_VALUE_SOURCES = [
    'id::nectar.suppliers.app_manifest_defaults',
    'id::nectar.suppliers.app_manifest_variables'
    # 'id::nectar.suppliers.current_step_inlines'
  ]

  def __init__(self, config):
    super().__init__(config)
    self.observer.progress = ProgressItem(
      id='apply_manifest',
      status='running',
      title="Apply Resources",
      info="Updates the manifest and waits for a settled state",
      sub_items=[
        *ApplyManifestActionPart.progress_items(),
        *AwaitPredicatesSettleActionPart.progress_items()
      ]
    )

  def compute_values(self) -> Dict:
    if isinstance(self.value_sources, dict):
      return self.resolve_prop_value(self.value_sources)
    else:
      dicts = [self.resolve_prop_value(s) for s in self.value_sources]
      return deep_merge(*dicts)

  @cached_property
  def value_sources(self) -> Union[KoD, List[KoD]]:
    return self.get_prop(self.KEY_VALUES, self.DEFAULT_VALUE_SOURCES)

  @cached_property
  def tam(self) -> TamDict:
    return self.get_prop(self.KEY_TAM, config_man.tam())

  @cached_property
  def res_selectors(self) -> List:
    return self.inflate_children(
      ResourceSelector,
      prop=self.KEY_APPLY_FILTERS
    )

  def perform(self, **kwargs) -> bool:
    outcomes = ApplyManifestActionPart.perform(
      tam=self.tam,
      values=self.compute_values(),
      observer=self.observer,
      selectors=self.res_selectors
    )

    AwaitPredicatesSettleActionPart.perform(
      self.observer,
      PredicateFactory.from_apply_outcome(outcomes)
    )

    self.observer.on_succeeded()
    return True
