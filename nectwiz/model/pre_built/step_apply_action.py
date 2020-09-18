from typing import Dict

from nectwiz.core.core.types import ActionOutcome, StepActionKwargs
from nectwiz.core.tam.tam_provider import tam_client
from nectwiz.model.action.action import Action


class StepApplyResAction(Action):

  def __init__(self, config):
    super().__init__(config)
    self.res_selectors = config.get('cmd', [])

  def perform(self, **kwargs: StepActionKwargs) -> Dict:
    inline_assigns = kwargs.get('inline', {})
    out = tam_client().apply(self.res_selectors, inline_assigns.items())
    logs = out.split("\n") if out else []
    #todo move predicate logic to here
    return dict(logs=[l for l in logs if l])
