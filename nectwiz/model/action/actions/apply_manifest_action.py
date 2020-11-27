from typing import Optional

from nectwiz.core.core.types import TamDict, ProgressItem
from nectwiz.model.action.action_parts.apply_manifest_action_part \
  import ApplyManifestActionPart
from nectwiz.model.action.action_parts.await_predicates_settle_action_part \
  import AwaitPredicatesSettleActionPart
from nectwiz.model.action.base.action import Action
from nectwiz.model.factory.predicate_factories import PredicateFactory


class ApplyManifestAction(Action):
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

    self.res_selectors = config.get('apply_filters', [])
    self.tam: Optional[TamDict] = config.get('tam')
    self.values_source_key = config.get('values_source_key')
    self.values_root_key = config.get('values_root_key')
    self.inlines = {}

  def perform(self, **kwargs) -> bool:
    self.inlines = kwargs.get('inlines')

    outcomes = ApplyManifestActionPart.perform(
      observer=self.observer,
      constructor_kwargs=dict(
        tam=self.tam,
        values_source_key=self.values_source_key,
        values_root_key=self.values_root_key
      ),
      selectors=self.res_selectors,
      inlines=self.inlines
    )

    AwaitPredicatesSettleActionPart.perform(
      self.observer,
      PredicateFactory.from_apply_outcome(outcomes)
    )

    self.observer.on_succeeded()
    return True
