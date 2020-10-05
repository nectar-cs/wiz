from functools import lru_cache
from typing import Dict, Optional

from nectwiz.core.core.types import ErrDict, KoD
from nectwiz.model.base.resource_selector import ResourceSelector
from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.error.error_context import ErrCxt


class ErrorTriggerSelector(WizModel):
  def __init__(self, config: Dict):
    super().__init__(config)
    self.prop_selector: Dict = config.get('property_selector', {})
    self.res_sel_kod: KoD = config.get('resource_selector', {})

  def match_confidence_score(self, errctx: ErrCxt) -> int:
    score = 0
    prop_match_result = self.prop_match_score(errctx)
    if prop_match_result is not None:
      score += prop_match_result
      res_match_result = self.res_match_score(errctx)
      if res_match_result is not None:
        score += res_match_result
      else:
        return 0
    else:
      return 0

  def prop_match_score(self, errctx: ErrCxt) -> Optional[int]:
    challenge = errctx.selectable_properties()
    matches = 0
    for prop, check_against in self.prop_selector.items():
      if prop in challenge.keys():
        if challenge[prop] in check_against:
          matches += 1
        else:
          return None
    return matches

  def res_match_score(self, errctx: ErrCxt):
    if self.res_selector():
      if errctx.resource():
        selector, resource = self.res_selector(), errctx.resource().raw
        if selector.selects_res(resource, {}):
          return 1
      return None
    else:
      return 0

  @lru_cache
  def res_selector(self) -> ResourceSelector:
    if self.res_sel_kod:
      return ResourceSelector.inflate(self.res_sel_kod)
