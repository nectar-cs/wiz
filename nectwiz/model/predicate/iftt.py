from typing import TypeVar, Dict, List, Optional

from nectwiz.core.core.config_man import config_man
from nectwiz.core.core.types import KoD
from nectwiz.model.base.wiz_model import WizModel


T = TypeVar('T', bound='WizModel')
class Iftt(WizModel):

  def __init__(self, config: Dict):
    super().__init__(config)
    self.choice_items: List[Dict] = config.get('items', [])

  def resolve_item(self) -> Optional[KoD]:
    from nectwiz.model.predicate.predicate import Predicate
    for it in self.choice_items:
      predicate_kod, value = it.get('predicate'), it.get('value')
      if predicate_kod:
        predicate = self.inflate_child(Predicate, predicate_kod)
        if predicate.evaluate():
          return value
    print(f"[nectwiz:iftt_matrix] {self.config} all predicates negative")
    return None
