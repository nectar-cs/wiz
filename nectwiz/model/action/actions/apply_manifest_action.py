from typing import Optional

from nectwiz.core.core.types import StepActionKwargs, TamDict, ProgressItem
from nectwiz.model.action.action_parts.apply_manifest_action_part import ApplyManifestActionPart
from nectwiz.model.action.action_parts.await_settled_action_part import AwaitSettledActionPart
from nectwiz.model.action.base.action import Action


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
        *AwaitSettledActionPart.progress_items()
      ]
    )

    self.res_selectors = config.get('apply_filters', [])
    self.tam: Optional[TamDict] = config.get('tam')
    self.values_source_key = config.get('values_source_key')
    self.values_root_key = config.get('values_root_key')

  def perform(self, **kwargs: StepActionKwargs) -> bool:
    outcomes = ApplyManifestActionPart.perform(
      observer=self.observer,
      tam=self.tam,
      selectors=self.res_selectors,
      inlines=(kwargs.get('inlines') or {}).items(),
      values_source_key=self.values_source_key,
      values_root_key=self.values_root_key
    )

    AwaitSettledActionPart.perform(
      self.observer,
      outcomes
    )

    self.observer.on_succeeded()
    return True
