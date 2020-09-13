from nectwiz.core.core.types import UpdateDict, ActionOutcome
from nectwiz.core.telem import updates_man
from nectwiz.model.action.action import Action


class AppUpdateAction(Action):
  def perform(self, **update: UpdateDict):
    outcome = updates_man.perform_update(update)
    return ActionOutcome(
      **super().outcome_template(),
      charge='positive',
      data=outcome
    )
