from typing import Dict

from k8kat.res.base.kat_res import KatRes
from werkzeug.utils import cached_property

from nectwiz.core.core.config_man import config_man
from nectwiz.core.core.types import ProgressItem
from nectwiz.model.action.base.action import Action
from nectwiz.model.base.resource_selector import ResourceSelector


key_main = 'delete_resources'

class DeleteResourcesAction(Action):

  RES_SELECTORS_KEY = 'resource_selectors'

  def __init__(self, config: Dict):
    super().__init__(config)
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

  @cached_property
  def resource_selectors(self):
    return self.inflate_children(
      ResourceSelector,
      prop=self.RES_SELECTORS_KEY
    )

  def perform(self, *args, **kwargs) -> bool:
    self.observer.set_item_status(key_main, 'running')
    context = dict(resolvers=config_man.resolvers())
    victims = []

    for selector in self.resource_selectors:
      victims += selector.query_cluster(context)

    for victim in victims:
      item = make_item(victim)
      self.observer.add_subitem(key_main, item)
      victim.delete()
      self.observer.subitem(key_main, item['id'])['status'] = 'positive'
    self.observer.set_item_status(key_main, 'positive')

    return True

def make_item(res: KatRes):
  return dict(
    id=f"{res.res_name_plural}/{res.name}",
    title=f"Delete {res.res_name_plural}/{res.name}",
    status='running'
  )
