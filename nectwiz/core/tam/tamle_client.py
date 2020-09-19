import subprocess
from typing import Dict, List

import yaml

from nectwiz.core.core.types import K8sResDict
from nectwiz.core.core.config_man import config_man

from nectwiz.core.tam.tam_client import TamClient, fmt_inline_assigns


class TamleClient(TamClient):
  def load_manifest_defaults(self) -> Dict[str, str]:
    raw = exec_cmd('values')
    return yaml.load(raw, Loader=yaml.FullLoader)

  def load_tpd_manifest(self, inlines=None) -> List[K8sResDict]:
    formatted_inlines = fmt_inline_assigns(inlines or [])
    raw = exec_cmd(f'template {formatted_inlines} {flags()}')
    return list(yaml.load_all(raw, Loader=yaml.FullLoader))


def flags():
  return f"--set namespace={config_man.ns()}"


def exec_cmd(cmd):
  uri, ver = config_man.tam()['uri'], config_man.tam()['version']
  exec_name = f"{uri}-{ver}" if ver else uri
  full_cmd = f"{exec_name} {cmd}".split(" ")
  return subprocess.check_output(full_cmd).decode('utf-8')
