from typing import Dict

from nectwiz.core.core.types import UpdateDict, ActionOutcome
from nectwiz.core.telem import updates_man
from nectwiz.model.action.action import Action


class AppUpdateAction(Action):
  def perform(self) -> Dict:
    return updates_man.install_next_available()
