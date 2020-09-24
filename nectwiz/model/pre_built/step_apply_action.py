from typing import Dict

from nectwiz.core.core import utils
from nectwiz.core.core.types import StepActionKwargs
from nectwiz.core.tam.tam_provider import tam_client
from nectwiz.model.action.action import Action


class StepApplyResAction(Action):

  def __init__(self, config):
    super().__init__(config)
    self.res_selectors = config.get('apply_only', [])

  def perform(self, **kwargs: StepActionKwargs) -> Dict:
    inlines = (kwargs.get('inline') or {}).items()
    tam = kwargs.get('tam')
    
    out = tam_client(tam).apply(self.res_selectors, inlines)

    logs = utils.clean_log_lines(out)
    #todo move predicate logic to here
    return dict(logs=logs)
