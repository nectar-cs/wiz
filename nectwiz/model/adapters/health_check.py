from typing import Dict, List

from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.predicate.predicate import Predicate


class HealthChecksAdapter(WizModel):
  def __init__(self, config: Dict):
    super().__init__(config)
    self.use_liveness = config.get('use_liveness', True)

  def predicates(self) -> List[Predicate]:
    expl_children = self.load_children('predicates', Predicate)
    return [
      *self.gen_liveness_predicates(),
      expl_children
    ]

  def gen_liveness_predicates(self) -> List[Predicate]:
    pass
