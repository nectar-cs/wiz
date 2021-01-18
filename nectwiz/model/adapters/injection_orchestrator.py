from typing import List

from werkzeug.utils import cached_property

from nectwiz.model.base.resource_selector import ResourceSelector
from nectwiz.model.base.wiz_model import WizModel


class InjectionOrchestrator(WizModel):

  RES_SELECTORS_KEY = 'apply_selectors'

  @classmethod
  def singleton_id(cls):
    return 'nectar.injection-orchestrators.main'

  @cached_property
  def apply_selectors(self) -> List[ResourceSelector]:
    return self.inflate_children(
      ResourceSelector,
      prop=self.RES_SELECTORS_KEY
    )
