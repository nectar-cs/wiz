import subprocess
from typing import Dict, List

import yaml

from nectwiz.core.core.types import K8sResDict, TamDict
from nectwiz.core.core.config_man import config_man

from nectwiz.core.tam.tam_client import TamClient, fmt_inline_assigns


class TamleClient(TamClient):
  def load_manifest_defaults(self) -> Dict[str, str]:
    raw = exec_cmd(self.tam, 'values')
    return yaml.load(raw, Loader=yaml.FullLoader)

  def load_templated_mfst(self, inlines=None) -> List[K8sResDict]:
    formatted_inlines = fmt_inline_assigns(inlines or [])
    raw = exec_cmd(self.tam, f'template {formatted_inlines} {flags()}')
    return list(yaml.load_all(raw, Loader=yaml.FullLoader))


def flags():
  return f"--set namespace={config_man.ns()}"


def exec_cmd(tam: TamDict, cmd):
  uri, ver = tam['uri'], tam['version']
  exec_name = f"{uri}-{ver}" if ver else uri
  print(f"Local exec name {exec_name}")
  full_cmd = f"{exec_name} {cmd}".split(" ")
  output = subprocess.check_output(full_cmd).decode('utf-8')
  print(f"{full_cmd} -> {output}")
  return output
