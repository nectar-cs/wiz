from typing import Dict, List, Tuple

import yaml

from nectwiz.core.tam import tami_prep
from nectwiz.core.tam.tam_client import TamClient, fmt_inline_assigns
from nectwiz.core.types import K8sResDict
from nectwiz.core.wiz_app import wiz_app

interpolate_cmd = "pipenv run python3 app.py kerbi interpolate"
tami_name_key = 'tami_name'
vars_full_path = f'{tami_prep.vars_mount_dir}/{tami_prep.vars_file_name}'


class TamiClient(TamClient):

  def load_manifest_defaults(self) -> Dict[str, str]:
    pod_args_str = f"values {wiz_app.tam().get('args', '')}"
    pod_args = [v for v in pod_args_str.split(' ') if v]
    result = tami_prep.consume(wiz_app.ns(), image_name(), pod_args)
    return yaml.load(result, Loader=yaml.FullLoader)

  def load_tpd_manifest(self, inlines=None) -> List[K8sResDict]:
    """
    Creates a Kubernetes pod running the vendor-specified image, then reads the
    output logs, expected to be a string literal of the interpolated application manifest.
    :param inlines:
    :return: parsed logs from the Tami container.
    """
    pod_args = ['template'] + gen_tami_args(inlines)
    result = tami_prep.consume(wiz_app.ns(), image_name(), pod_args)
    return list(yaml.load_all(result, Loader=yaml.FullLoader))


def gen_tami_args(inline_assigns) -> List[str]:
  """
  Generates arguments to pass to the Tami image at startup.
  :param inline_assigns: desired inline assigns.
  :return: list of flags to pass to Tami image.
  """
  inlines = default_inlines() + (inline_assigns or [])
  values_flag: str = f"-f {vars_full_path}"
  vendor_flags: str = wiz_app.tam().get('args')
  inline_flags: str = fmt_inline_assigns(inlines)
  all_flags: str = f"{values_flag} {inline_flags} {vendor_flags}"
  return [w for w in all_flags.split(" ") if w]


def image_name():
  image_base = wiz_app.tam()['uri']
  if ":" in image_base:
    return image_base
  else:
    version = wiz_app.tam().get('ver', 'latest')
    return f"{image_base}:{version}"


def default_inlines() -> List[Tuple[str, any]]:
  return [('namespace', wiz_app.ns())]
