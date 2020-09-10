import os
from typing import Dict, List

from nectwiz.core.core import utils

tami_pod_name = 'tami'
cache_root = '/tmp'


def default_configs() -> List[Dict]:
  """
  Gets the pre-built configs, converting from YAMLs to dicts.
  :return: dictionary containing pre-built configs.
  """
  pwd = os.path.join(os.path.dirname(__file__))
  return utils.yamls_in_dir(f"{pwd}/../../model/pre_built")




class WizApp:

  def __init__(self):
    self.tam_client_override = None
    self.jobs_backend = 'rq'

  def uses_rq(self):
    return self.jobs_backend == 'rq'

  def uses_sync(self):
    return self.jobs_backend == 'sync'


wiz_app = WizApp()
