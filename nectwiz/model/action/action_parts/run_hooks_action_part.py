from typing import List

from nectwiz.core.core.types import ProgressItem
from nectwiz.model.action.base.observer import Observer
from nectwiz.model.hook.hook import Hook


class RunHookGroupActionPart:

  @staticmethod
  def progress_items(which: str):
    return [
      ProgressItem(
        id=f'{which}_hooks',
        status='idle',
        title=f'{which}-update Hooks'.title(),
        info='Run vendor-provided hooks, halt on fatal error',
        sub_items=[]
      ),
    ]

  @classmethod
  def perform(cls, observer: Observer, which: str, hooks: List[Hook]):
    cls.on_group_started(observer, which, hooks)
    for hook in hooks:
      outcome = hook.run()
      cls.on_hook_finished(observer, which, hook, outcome)
      cls.check_hook_failed(observer, which, hook, outcome)
    observer.set_item_status(f'{which}_hooks', 'positive')

  @classmethod
  def on_hook_started(cls, observer: Observer):
    observer.item('perform')['status'] = 'running'
    observer.notify_job()

  @classmethod
  def check_hook_failed(cls, observer: Observer, which: str, hook: Hook, outcome):
    if not outcome:
      observer.process_error(
        fatal=hook.abort_on_fail,
        tone='warning',
        reason=f'Hook {hook.title} failed',
        event_type='run_hooks',
        which_hook=which,
        hook_id=hook.id()
      )

  @classmethod
  def on_hook_finished(cls, observer: Observer, which: str, hook: Hook, outcome):
    status = 'positive' if outcome else 'negative'
    observer.set_subitem_status(f'{which}_hooks', hook.id(), status)

  @classmethod
  def on_group_started(cls, observer: Observer, which: str, hooks: List[Hook]):
    sub_items = list(map(gen_hook_empty_subitem, hooks))
    observer.set_prop(f'{which}_hooks', 'sub_items', sub_items)
    observer.set_item_status(f'{which}_hooks', 'running')

def gen_hook_empty_subitem(hook: Hook):
  return dict(
    id=hook.id(),
    status='idle',
    title=hook.title
  )
