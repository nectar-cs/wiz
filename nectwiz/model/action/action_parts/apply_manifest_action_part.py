import time

import yaml

from nectwiz.core.core import utils
from nectwiz.core.core.types import ProgressItem, KAOs
from nectwiz.core.tam.tam_provider import tam_client
from nectwiz.model.action.base.observer import Observer, simple_action_eval

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
  def perform(cls, **kwargs):
    """
    Keyword Args:
      observer Observer: parent observer
      values Dict: values to be passed to the templating engine
      selectors List[ResSelector] list of resource discriminators
      tam TamDict: templating engine descriptor
    """
    observer: Observer = kwargs['observer']
    values = kwargs['values']
    selectors = kwargs['selectors']
    client = tam_client(tam=kwargs['tam'])

    with simple_action_eval(observer, key_load_manifest):
      res_descs = client.template_manifest(values)
      res_descs = client.filter_res(res_descs, selectors)
      observer.log(list(map(yaml.dump, res_descs)))

    with simple_action_eval(observer, key_apply_manifest):
      outkomes = client.kubectl_apply(res_descs)
      observer.set_prop(key_apply_manifest, 'data', {'outcomes': outkomes})
      observer.log(list(map(utils.kao2log, outkomes)))
      cls.check_kao_failures(observer, outkomes)

    time.sleep(1)
    return outkomes

  @classmethod
  def check_kao_failures(cls, observer: Observer, outcomes: KAOs):
    fail_finder = lambda kao: kao.get('error') is not None
    kao_culprit = next(filter(fail_finder, outcomes), None)
    if kao_culprit is not None:
      observer.process_error(
        fatal=True,
        tone='error',
        reason='kubectl apply failed for one or more resources.',
        type='manifest_apply_failed',
        resource=dict(
          name=kao_culprit.get('name'),
          kind=kao_culprit.get('kind')
        ),
        logs=[kao_culprit.get('error')]
      )
