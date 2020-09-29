import time
from typing import Dict

from k8kat.res.base.kat_res import KatRes

from nectwiz.core.core.config_man import config_man
from nectwiz.core.core.types import ProgressItem
from nectwiz.model.action.action import Action
from nectwiz.model.base.resource_selector import ResourceSelector


class DeleteResourcesAction(Action):

  def __init__(self, config: Dict):
    super().__init__(config)
    self.selector_desc = config.get('selector')
    self.observer.progress = ProgressItem(
      sub_items=[
        ProgressItem(
          id='delete_resources',
          title='Delete Resources',
          status='idle',
          info='Delete resources one by one',
          sub_items=[]
        )
      ]
    )

  def perform(self, *args, **kwargs) -> Dict:
    selector = ResourceSelector.inflate(self.selector_desc)
    context = dict(resolvers=config_man.resolvers())
    victims = selector.query_cluster(context)
    self.observer.set_item_status('delete_resources', 'running')

    for victim in victims:
      item = make_item(victim)
      self.observer.add_subitem('delete_resources', item)
      print(f"Dream of delete {victim.name}")
      time.sleep(2)
      self.observer.subitem('delete_resources', item['id'])['status'] = 'positive'

    self.observer.set_item_status('delete_resources', 'positive')

    return {}

def make_item(res: KatRes):
  return dict(
    id=f"{res.res_name_plural}/{res.name}",
    title=f"Delete {res.res_name_plural}/{res.name}",
    status='running'
  )
