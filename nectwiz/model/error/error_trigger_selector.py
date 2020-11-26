from typing import Dict, Optional

from werkzeug.utils import cached_property

from nectwiz.model.base.resource_selector import ResourceSelector
from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.error.error_context import ErrCtx


class ErrorTriggerSelector(WizModel):
  PROP_SELECTOR_KEY = 'property_selector'
  RES_SELECTOR_KEY = 'resource_selector'

  @cached_property
  def prop_selector(self) -> Dict:
    return self.get_prop(self.PROP_SELECTOR_KEY, {})

  @cached_property
  def res_selector(self) -> ResourceSelector:
    return self.inflate_child(
      ResourceSelector,
      prop=self.RES_SELECTOR_KEY,
      safely=True
    ) or self.inflate_child(ResourceSelector, kod="*:*")

  def match_confidence_score(self, errctx: ErrCtx) -> int:
    prop_match_result = self.prop_match_score(errctx)
    if prop_match_result is not None:
      res_match_result = self.res_match_score(errctx)
      if res_match_result is not None:
        return prop_match_result + res_match_result
      else:
        return 0
    else:
      return 0

  def prop_match_score(self, errctx: ErrCtx) -> Optional[int]:
    challenge = errctx.selectable_properties
    matches = 0
    for prop, check_against in self.prop_selector.items():
      if prop in challenge.keys():
        if challenge[prop] in check_against:
          matches += 1
        else:
          return None
    return matches

  def res_match_score(self, errctx: ErrCtx) -> Optional[int]:
    if self.res_selector:
      if errctx.resource_dict:
        if self.res_selector.selects_res(errctx.resource_dict):
          return 1
      return None
    else:
      return 0
