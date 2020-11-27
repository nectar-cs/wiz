import traceback
from typing import List

from werkzeug.utils import cached_property

from nectwiz.core.core.types import ProgressItem
from nectwiz.model.action.base.action import Action
from nectwiz.model.predicate.predicate import Predicate


class RunPredicatesAction(Action):

  PREDICATES_KEY = 'predicates'

  @cached_property
  def predicates(self) -> List[Predicate]:
    return self.inflate_children(Predicate, prop=self.PREDICATES_KEY)

  def perform(self):
    self.observer.set_items(list(map(pred2subitem, self.predicates)))
    error_count = 0
    for predicate in self.predicates:
      self.observer.set_item_running(predicate.id())
      result = None
      exc_dump = None
      # noinspection PyBroadException
      try:
        result = predicate.evaluate()
      except:
        exc_dump = traceback.format_exc()
        print(traceback.format_exc())
        print("[nectwiz::predicate_action] count internal error as fail ^^")

      self.observer.set_item_outcome(predicate.id(), result)
      if not result:
        self.observer.blame_item_id = predicate.id()
        error_count += 1
        self.observer.process_error(
          fatal=False,
          type='internal_error' if exc_dump else 'negative_predicate',
          event_type='predicate_eval',
          tone=predicate.tone,
          reason=predicate.reason,
          logs=[exc_dump] if exc_dump else [],
          extras=predicate.error_extras(),
          resource=predicate.culprit_res_signature()
        )
    self.observer.on_ended(error_count == 0)
    return error_count == 0


def pred2subitem(predicate: Predicate) -> ProgressItem:
  return ProgressItem(
    id=predicate.id(),
    title=predicate.title,
    info=predicate.info,
    status='idle',
    sub_items=[],
    error={}
  )
