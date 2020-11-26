from functools import lru_cache
from typing import List, Dict

from werkzeug.utils import cached_property

from nectwiz.model.action.actions.run_predicates_action import RunPredicatesAction
from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.operation.stage import Stage


class Operation(WizModel):

  STAGES_KEY = 'stages'
  SYNOPSIS_KEY = 'synopsis'
  PREFLIGHT_PREDS_KEY = 'preflight_predicates'

  @cached_property
  def synopsis(self) -> str:
    return self.get_prop(self.SYNOPSIS_KEY) or self.title

  def is_system(self) -> bool:
    return self.id() in ['installation', 'uninstall']

  def preflight_action_config(self) -> Dict:
    return dict(
      kind=RunPredicatesAction.__name__,
      predicates=self.config.get(self.PREFLIGHT_PREDS_KEY)
    )

  def has_preflight_checks(self) -> bool:
    return self.config.get(self.PREFLIGHT_PREDS_KEY) is not None

  @cached_property
  def stages(self) -> List[Stage]:
    """
    Loads the Stages associated with the Operation.
    :return: list of Stage instances.
    """
    return self.inflate_children(Stage, prop=self.STAGES_KEY)

  def stage(self, stage_id: str) -> Stage:
    """
    Finds the Stage by key and inflates (instantiates) into a Stage instance.
    :param stage_id: identifier for desired Stage.
    :return: Stage instance.
    """
    matcher = lambda stage: stage.id() == stage_id
    return next(filter(matcher, self.stages), None)
