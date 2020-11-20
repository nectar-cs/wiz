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
    self.var_root = Optional[str] = config.get('var_root')

  def perform(self, **kwargs: StepActionKwargs) -> bool:
    inlines = (kwargs.get('inline') or {}).items()
    outcomes = ApplyManifestActionPart.perform(
      self.observer,
      self.tam,
      self.res_selectors,
      inlines
    )
    AwaitSettledActionPart.perform(
      self.observer,
      outcomes
    )
    self.observer.on_succeeded()
    return True
