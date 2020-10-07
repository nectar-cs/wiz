from typing import Dict

from nectwiz.core.core.config_man import config_man
from nectwiz.core.core.types import ProgressItem
from nectwiz.model.action.base.action import Action
from nectwiz.model.action.base.observer import Observer
from nectwiz.model.predicate.predicate import Predicate


class RunPredicatesAction(Action):
  def __init__(self, config: Dict):
    super().__init__(config)
    self.observer = Observer()
    self.predicates = self.load_children('predicates', Predicate)
    self.observer.set_items(list(map(pred2subitem, self.predicates)))

  def perform(self):
    context = dict(resolvers=config_man.resolvers())
    error_count = 0
    for predicate in self.predicates:
      self.observer.set_item_running(predicate.id())
      result = predicate.evaluate(context)
      self.observer.set_item_outcome(predicate.id(), result)
      if not result:
        self.observer.blame_item_id = predicate.id()
        error_count += 1
        self.observer.process_error(
          fatal=False,
          event_type='predicate_eval',
          predicate_id=predicate.id(),
          predicate_kind=predicate.kind(),
          tone=predicate.tone,
          reason=predicate.reason,
          **predicate.error_extras()
        )
    self.observer.on_ended(error_count == 0)


def pred2subitem(predicate: Predicate) -> ProgressItem:
  return ProgressItem(
    id=predicate.id(),
    title=predicate.title,
    info=predicate.info,
    status='idle',
    sub_items=[],
    error={}
  )
