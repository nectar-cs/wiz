from typing import Dict, List, Tuple

import yaml

from nectwiz.core.tam import tami_prep
from nectwiz.core.tam.tam_client import TamClient, fmt_inline_assigns
from nectwiz.core.core.types import K8sResDict, TamDict
from nectwiz.core.core.config_man import config_man

interpolate_cmd = "pipenv run python3 app.py kerbi interpolate"
tami_name_key = 'tami_name'
vars_full_path = f'{tami_prep.vars_mount_dir}/{tami_prep.vars_file_name}'


class TamiClient(TamClient):

  def load_manifest_defaults(self) -> Dict[str, str]:
    pod_args_str = f"values {config_man.tam().get('args', '')}"
    pod_args = [v for v in pod_args_str.split(' ') if v]
    ns, image = config_man.ns(), image_name(config_man.tam())
    result = tami_prep.consume(ns, image, pod_args)
    return yaml.load(result, Loader=yaml.FullLoader)

  def load_tpd_manifest(self, inlines=None) -> List[K8sResDict]:
    """
    Creates a Kubernetes pod running the vendor-specified image, then reads the
    output logs, expected to be a string literal of the interpolated application manifest.
    :param inlines:
    :return: parsed logs from the Tami container.
    """
    pod_args = ['template'] + gen_tami_args(inlines)
    ns, image = config_man.ns(), image_name(config_man.tam())
    result = tami_prep.consume(ns, image, pod_args)
    if not result:
      print(f"[nectwiz::tami_client]Fatal tami returned {result}!")
    return list(yaml.load_all(result, Loader=yaml.FullLoader))


def gen_tami_args(inline_assigns) -> List[str]:
  """
  Generates arguments to pass to the Tami image at startup.
  :param inline_assigns: desired inline assigns.
  :return: list of flags to pass to Tami image.
  """
  inlines = default_inlines() + (inline_assigns or [])
  values_flag: str = f"-f {vars_full_path}"
  vendor_flags: str = config_man.tam().get('args')
  inline_flags: str = fmt_inline_assigns(inlines)
  all_flags: str = f"{values_flag} {inline_flags} {vendor_flags}"
  return [w for w in all_flags.split(" ") if w]


def image_name(tam: TamDict):
  given_name = tam['uri']
  version = tam.get('version') or 'latest'
  if ":" in given_name:
    clean_name = given_name.split(':')[0]
    hardcoded_ver = given_name.split(':')[1]
    version = tam.get('version') or  hardcoded_ver or 'latest'
  else:
    clean_name = given_name
  return f"{clean_name}:{version}"


def default_inlines() -> List[Tuple[str, any]]:
  return [('namespace', config_man.ns())]
