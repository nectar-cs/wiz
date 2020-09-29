from typing import Dict

from nectwiz.model.action.action import Action
from nectwiz.model.base.resource_selector import ResourceSelector


class DeleteResourcesAction(Action):

  def __init__(self, config: Dict):
    super().__init__(config)
    self.selector_desc = config.get('selector')

  def perform(self, *args, **kwargs) -> Dict:
    selector = ResourceSelector.inflate(self.selector_desc)
    victims = selector.query_cluster()
    for victim in victims:
      print(f"Dream of delete {victim.name}")
    return {}
