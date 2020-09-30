from typing import Dict

from nectwiz.core.core.config_man import config_man
from nectwiz.core.core.types import ProgressItem
from nectwiz.model.action.action import Action
from nectwiz.model.predicate.predicate import Predicate


class RunPredicatesAction(Action):

  def __init__(self, config: Dict):
    super().__init__(config)
    self.predicates = self.load_children('predicates', Predicate)
    for predicate in self.predicates:
      self.observer.progress['sub_items'].append(
        ProgressItem(
          id=predicate.id(),
          title=predicate.title,
          info=predicate.info,
          status='idle',
          sub_items=[]
        )
      )

  def perform(self):
    context = dict(resolvers=config_man.resolvers())
    for predicate in self.predicates:
      self.observer.set_item_running(predicate.id())
      result = predicate.evaluate(context)
      self.observer.set_item_outcome(predicate.id(), result)
      self.observer.item(predicate.id())['data'] = dict(
        tone=predicate.tone,
        reason=predicate.reason
      )
    self.observer.on_succeeded()
