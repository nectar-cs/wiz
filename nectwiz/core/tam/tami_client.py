from typing import Dict, List

import yaml

from nectwiz.core.core.config_man import config_man
from nectwiz.core.core.types import K8sResDict, TamDict
from nectwiz.core.tam import tami_prep
from nectwiz.core.tam.tam_client import TamClient

vars_full_path = f"{tami_prep.values_mount_dir}/" \
                 f"{tami_prep.values_file_path}"


class TamiClient(TamClient):

  def load_manifest_defaults(self) -> Dict[str, str]:
    pod_args_str = f"show values . {self.any_cmd_args()}"
    pod_args = [v for v in pod_args_str.split(' ') if v]
    ns, image = config_man.ns(), image_name(self.tam)
    result = tami_prep.consume(
      ns=ns,
      image=image,
      arglist=pod_args,
      values=None
    )
    return yaml.load(result, Loader=yaml.FullLoader)

  def load_templated_manifest(self, inlines: Dict) -> List[K8sResDict]:
    """
    Creates a Kubernetes pod running the vendor-specified image, then reads the
    output logs, expected to be a string literal of the interpolated application manifest.
    :param inlines:
    :return: parsed logs from the Tami container.
    """
    ns, image = config_man.ns(), image_name(self.tam)
    template_cmd_part = self.template_cmd_args(inlines, vars_full_path)
    pod_args = ['template', *template_cmd_part.split(' ')]
    result = tami_prep.consume(
      ns=ns,
      image=image,
      arglist=pod_args,
      values=self.compute_values()
    )

    if result:
      return list(yaml.load_all(result, Loader=yaml.FullLoader))
    else:
      raise TamiNonStarterError("Could not start TAMI pod")

def image_name(tam: TamDict):
  given_name = tam['uri']
  version = tam.get('version') or 'latest'
  if ":" in given_name:
    clean_name = given_name.split(':')[0]
    hardcoded_ver = given_name.split(':')[1]
    version = tam.get('version') or hardcoded_ver or 'latest'
  else:
    clean_name = given_name
  return f"{clean_name}:{version}"


class TamiNonStarterError(Exception):
  pass
