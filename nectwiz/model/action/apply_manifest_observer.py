from nectwiz.core.core.types import TamDict, ProgressItem, KAOs
from nectwiz.model.action.action_observer import ActionObserver


class ApplyManifestObserver(ActionObserver):
  def __init__(self, tam: TamDict, fail_fast=True):
    super().__init__(fail_fast=fail_fast)
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

  def on_apply_finished(self, outcomes: KAOs):
    self.item('apply')['data'] = {'outcomes': outcomes}
    self.check_kao_failures(outcomes)
    self.item('apply')['status'] = 'positive'
    self.item('await_settled')['status'] = 'running'
    self.notify_job()

  def on_settled(self, status: str):
    self.item('await_settled')['status'] = status
    self.notify_job()

  def get_kaos(self) -> KAOs:
    return self.item('apply').get('data', [])
