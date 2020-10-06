from typing import Dict, Optional

from nectwiz.core.core.config_man import config_man
from nectwiz.core.core.types import StepActionKwargs, TamDict, ProgressItem
from nectwiz.model.action.action import Action
from nectwiz.model.action.apply_manifest_action_part import ApplyManifestActionPart
from nectwiz.model.action.apply_manifest_observer import ApplyManifestObserver
from nectwiz.model.action.await_settled_action_part import AwaitSettledActionPart


class ApplyManifestAction(Action):
  def __init__(self, config):
    super().__init__(config)
    self.progress = ProgressItem(
      id=None,
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
    self.observer = ApplyManifestObserver(self.tam or config_man.tam())

  def perform(self, **kwargs: StepActionKwargs) -> Dict:
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
    return dict()
