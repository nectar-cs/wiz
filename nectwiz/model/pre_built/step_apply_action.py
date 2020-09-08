from nectwiz.core.tam.tam_provider import tam_client
from nectwiz.core.core.types import ActionOutcome, StepActionKwargs
from nectwiz.model.action.action import Action
from nectwiz.model.base.res_match_rule import ResMatchRule


class StepApplyResAction(Action):

  @classmethod
  def expected_key(cls):
    return "nectwiz.apply-resources"

  def perform(self, **kwargs: StepActionKwargs) -> ActionOutcome:
    inline_assigns = kwargs.get('inline_assigns')
    res_selector_descs = kwargs.get('res_selector_descs')
    res_selectors = list(map(ResMatchRule, res_selector_descs))

    out = tam_client().apply(res_selectors, inline_assigns.items())
    logs = out.split("\n") if out else []

    return ActionOutcome(
      charge='positive',
      summary=f'Applied {len(logs)} resources',
      data=dict(logs=logs)
    )
