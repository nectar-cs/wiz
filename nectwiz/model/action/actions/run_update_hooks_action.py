from typing import Dict, List

from werkzeug.utils import cached_property

from nectwiz.core.core import updates_man, utils
from nectwiz.core.core.types import ProgressItem, UpdateDict
from nectwiz.model.action.actions.multi_action import MultiAction
from nectwiz.model.action.base.action import Action
from nectwiz.model.hook.hook import Hook


class RunUpdateHooksAction(MultiAction):

  UPDATE_ID_KEY = 'update_id'
  TIMING_KEY = 'timing'

  @cached_property
  def timing(self) -> str:
    return self.get_prop(self.TIMING_KEY)

  @cached_property
  def update_bundle(self) -> UpdateDict:
    update_id = self.get_prop(self.UPDATE_ID_KEY)
    return updates_man.fetch_update(update_id)

  @cached_property
  def hooks(self) -> List[Hook]:
    return updates_man.find_hooks(self.timing, self.update_bundle)

  @cached_property
  def sub_actions(self) -> List[Action]:
    return utils.flatten([hook.actions for hook in self.hooks])
