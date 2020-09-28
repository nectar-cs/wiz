import json
import time
from typing import Dict, Optional, Union, List

from rq.job import Job, get_current_job

from nectwiz.core.core import utils
from nectwiz.core.core.config_man import config_man
from nectwiz.core.core.types import StepActionKwargs, ProgressItem, TamDict, PredEval
from nectwiz.core.tam.tam_client import save_manifest_as_tmp, kubectl_apply
from nectwiz.core.tam.tam_provider import tam_client
from nectwiz.model.action.action import Action
from nectwiz.model.predicate.default_predicates import from_apply_outcome
from nectwiz.model.step import status_computer
from nectwiz.model.step.step_state import StepState


class StepApplyResAction(Action):

  def __init__(self, config):
    super().__init__(config)
    self.res_selectors = config.get('apply_filters', [])
    self.tam: Optional[TamDict] = config.get('tam')
    self.observer = Observer(self.tam or config_man.tam())
    self.apply_logs: List[str] = []

  def perform(self, **kwargs: StepActionKwargs) -> Dict:
    inlines = (kwargs.get('inline') or {}).items()
    self.observer.notify_job()
    self.apply_part(inlines)
    self.await_part()
    self.observer.on_succeeded()
    return dict(logs=self.apply_logs)

  def apply_part(self, inlines):
    client = tam_client(self.tam)
    res_dicts = client.load_templated_manifest(inlines)
    save_manifest_as_tmp(res_dicts, self.res_selectors)
    self.observer.on_apply_started()
    out = kubectl_apply()
    print(out)
    self.apply_logs = utils.clean_log_lines(out)
    self.observer.on_apply_finished(self.apply_logs)
    time.sleep(2)

  def await_part(self):
    predicate_tree = from_apply_outcome(self.apply_logs)
    predicates = utils.flatten(predicate_tree.values())
    state = StepState('synthetic', None)
    context = dict(resolvers=config_man.resolvers())
    for i in range(120):
      status_computer.compute(predicate_tree, state, context)
      self.observer.on_exit_statuses_computed(predicates, state.exit_statuses)
      if state.has_settled():
        break
      else:
        time.sleep(2)

    print("DONE ONE DONE")
    print(state.status)
    self.observer.on_settled(state.status)
    return state.did_succeed()


class Observer:
  def __init__(self, tam: TamDict):
    self.progress = ProgressItem(
      id=None,
      status='running',
      title="Apply Resources",
      info="Updates the manifest and waits for a settled state",
      sub_items=[
        ProgressItem(
          id='load_manifest',
          status='running',
          title='Load Templated Manifest',
          info=f"From {tam.get('type')} {tam.get('uri')}",
          sub_items=[]
        ),
        ProgressItem(
          id='apply',
          status='idle',
          title='Run kubectl apply',
          info='Applies the templated manifest to the cluster',
          data={},
          sub_items=[]
        ),
        ProgressItem(
          id='await_settled',
          status='idle',
          title='Await Resources Settled',
          info='Wait until all changed resources are in a settled state',
          sub_items=[]
        ),
      ]
    )

  def on_apply_started(self):
    self.item('load_manifest')['status'] = 'positive'
    self.item('apply')['status'] = 'running'
    self.notify_job()

  def on_apply_finished(self, logs: List[str]):
    self.item('apply')['status'] = 'positive'
    self.item('await_settled')['status'] = 'running'
    self.item('apply')['data'] = {'outcomes': utils.logs2outkomes(logs)}
    self.notify_job()

  def on_exit_statuses_computed(self, predicates, statuses):
    flat_stats: List[Union[PredEval, ProgressItem]] = statuses['positive']
    for status in flat_stats:
      finder = lambda pred: pred.id() == status['predicate_id']
      originator = next(filter(finder, predicates), None)
      status['id'] = status['predicate_id']
      status['title'] = originator and originator.title
      status['info'] = originator and originator.info
      status['status'] = 'positive' if status['met'] else 'running'

    self.item('await_settled')['sub_items'] = flat_stats
    self.notify_job()

  def notify_job(self):
    job: Job = get_current_job()
    if job:
      job.meta['progress'] = json.dumps(self.progress)
      job.save_meta()

  def on_settled(self, status: str):
    self.item('await_settled')['status'] = status
    self.notify_job()

  def item(self, _id) -> Optional[ProgressItem]:
    finder = lambda item: item.get('id') == _id
    return next(filter(finder, self.progress['sub_items']), None)

  def on_succeeded(self):
    self.progress['status'] = 'positive'
    self.notify_job()
