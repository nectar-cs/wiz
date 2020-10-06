from nectwiz.core.core.types import TamDict, ProgressItem, KAOs
from nectwiz.model.action.action_observer import Observer
from nectwiz.model.action.await_settled_action_part import AwaitSettledActionPart


class ApplyManifestObserver(Observer):
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
        AwaitSettledActionPart.progress_item()
      ]
    )

  def get_kaos(self) -> KAOs:
    return self.item('apply').get('data', [])
