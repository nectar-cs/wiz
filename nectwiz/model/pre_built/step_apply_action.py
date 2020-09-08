from nectwiz.core.core.types import ActionOutcome, StepActionKwargs
from nectwiz.core.tam.tam_provider import tam_client
from nectwiz.model.action.action import Action


class StepApplyResAction(Action):

  def __init__(self, config):
    super().__init__(config)
    self.res_selectors = config.get('cmd')

  @classmethod
  def expected_id(cls):
    return "nectar.action.apply-resources"

  def perform(self, **kwargs: StepActionKwargs) -> ActionOutcome:
    print("MY ARGS ARE")
    print(kwargs)
    inline_assigns = kwargs.get('inline_assigns')

    out = tam_client().apply(self.res_selectors, inline_assigns.items())
    logs = out.split("\n") if out else []

    return ActionOutcome(
      **self.outcome_template(),
      charge='positive',
      summary=f'Applied {len(logs)} resources',
      data=dict(logs=logs)
    )