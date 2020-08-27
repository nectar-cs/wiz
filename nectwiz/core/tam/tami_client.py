from typing import Dict, List

import yaml

from nectwiz.core.tam import tami_prep
from nectwiz.core.tam.tam_client import TamClient, fmt_inline_assigns
from nectwiz.core.types import K8sResDict
from nectwiz.core.wiz_app import wiz_app

interpolate_cmd = "pipenv run python3 app.py kerbi interpolate"
tami_name_key = 'tami_name'


class TamiClient(TamClient):

  def load_manifest_defaults(self) -> Dict[str, str]:
    pod_args = ['values', wiz_app.tam()['args']]
    pod_args = [v for v in pod_args if v]
    result = tami_prep.consume(wiz_app.ns(), image_name(), pod_args)
    return yaml.load(result)

  def load_templated_manifest(self, inlines=None) -> List[K8sResDict]:
    """
    Creates a Kubernetes pod running the vendor-specified image, then reads the
    output logs, expected to be a string literal of the interpolated application manifest.
    :param inlines:
    :return: parsed logs from the Tami container.
    """
    pod_args = ['template'] + gen_tami_args(inlines)
    result = tami_prep.consume(wiz_app.ns(), image_name(), pod_args)
    return list(yaml.load_all(result, Loader=yaml.FullLoader))


def gen_tami_args(inlines) -> List[str]:
  """
  Generates arguments to pass to the Tami image at startup.
  :param inlines: desired inline assigns.
  :return: list of flags to pass to Tami image.
  """
  values_flag: str = "-f /values/master"
  vendor_flags: str = wiz_app.tam()['args']
  inline_flags: str = fmt_inline_assigns(inlines or {})
  all_flags: str = f"{values_flag} {inline_flags} {vendor_flags}"
  return all_flags.split(" ")


def image_name():
  return f"{wiz_app.tam()['uri']}:{wiz_app.tam()['ver']}"
