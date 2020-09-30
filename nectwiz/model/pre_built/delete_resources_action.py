import time
from typing import Dict

from k8kat.res.base.kat_res import KatRes

from nectwiz.core.core.config_man import config_man
from nectwiz.core.core.types import ProgressItem
from nectwiz.model.action.action import Action
from nectwiz.model.base.resource_selector import ResourceSelector


key_main = 'delete_resources'

class DeleteResourcesAction(Action):

  def __init__(self, config: Dict):
    super().__init__(config)
    self.selector_desc = config.get('selector')
    self.observer.progress = ProgressItem(
      sub_items=[
        ProgressItem(
          id=key_main,
          title='Delete Resources',
          status='idle',
          info='Delete resources one at a time',
          sub_items=[]
        )
      ]
    )

  def perform(self, *args, **kwargs) -> Dict:
    self.observer.set_item_status(key_main, 'running')
    selector = ResourceSelector.inflate(self.selector_desc)
    context = dict(resolvers=config_man.resolvers())
    victims = selector.query_cluster(context)

    for victim in victims:
      item = make_item(victim)
      self.observer.add_subitem(key_main, item)
      victim.delete()
      self.observer.subitem(key_main, item['id'])['status'] = 'positive'
    self.observer.set_item_status(key_main, 'positive')

    return {}

def make_item(res: KatRes):
  return dict(
    id=f"{res.res_name_plural}/{res.name}",
    title=f"Delete {res.res_name_plural}/{res.name}",
    status='running'
  )
