import json
import time
from typing import Optional

import yaml

from nectwiz.core.core import utils
from nectwiz.core.core.types import ProgressItem, KAOs, TamDict
from nectwiz.core.tam.tam_provider import tam_client
from nectwiz.model.action.base.observer import Observer

key_load_manifest = 'load_manifest'
key_apply_manifest = 'apply_manifest'

class ApplyManifestActionPart:
  @staticmethod
  def progress_items():
    return [
      ProgressItem(
        id=key_load_manifest,
        status='idle',
        title='Load Templated Manifest',
        info=f"Creates a pod loaded with the vendor manifest image",
        sub_items=[]
      ),
      ProgressItem(
        id=key_apply_manifest,
        status='idle',
        title='Run kubectl apply',
        info='Applies the templated manifest to the cluster',
        data={},
        sub_items=[]
      )
    ]

  @classmethod
  def perform(cls, observer: Observer, tam: Optional[TamDict], selectors, inlines):
    client = tam_client(tam)

    observer.set_item_status(key_load_manifest, 'running')
    manifestds = client.load_templated_manifest(inlines)
    manifestds = client.filter_res(manifestds, selectors)
    observer.set_item_status(key_load_manifest, 'positive')
    observer.log(list(map(yaml.dump, manifestds)))

    observer.set_item_status(key_apply_manifest, 'running')
    apply_outcomes = client.kubectl_apply(manifestds)
    cls.on_apply_finished(observer, apply_outcomes)
    observer.log(list(map(utils.kao2log, apply_outcomes)))
    cls.check_kao_failures(observer, apply_outcomes)

    time.sleep(2)
    return apply_outcomes

  @classmethod
  def on_apply_finished(cls, observer: Observer, outcomes: KAOs):
    observer.set_prop(key_apply_manifest, 'data', {'outcomes': outcomes})
    observer.set_item_status(key_apply_manifest, 'positive')

  @classmethod
  def check_kao_failures(cls, observer: Observer, outcomes: KAOs):
    observer.blame_item_id = key_apply_manifest
    fail_finder = lambda kao: kao.get('error') is not None
    kao_culprit = next(filter(fail_finder, outcomes), None)
    if kao_culprit is not None:
      observer.process_error(
        fatal=True,
        tone='error',
        reason='kubectl apply failed for one or more resources.',
        event_type='apply_manifest',
        resource=dict(
          name=kao_culprit.get('name'),
          kind=kao_culprit.get('kind')
        ),
        logs=[kao_culprit.get('error')]
      )
