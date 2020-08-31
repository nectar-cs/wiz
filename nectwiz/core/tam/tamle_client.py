import subprocess
from typing import Dict, List

import yaml

from nectwiz.core.types import K8sResDict
from nectwiz.core.wiz_app import wiz_app

from nectwiz.core.tam.tam_client import TamClient, fmt_inline_assigns


class TamleClient(TamClient):

  def load_manifest_defaults(self) -> Dict[str, str]:
    raw = exec_cmd('values')
    return yaml.load(raw, Loader=yaml.FullLoader)


  def load_tpd_manifest(self, inlines=None) -> List[K8sResDict]:
    formatted_inlines = fmt_inline_assigns(inlines or [])
    raw = exec_cmd(f'template {formatted_inlines}')
    return list(yaml.load_all(raw, Loader=yaml.FullLoader))


def exec_cmd(cmd):
  full_cmd = f"{wiz_app.tam()['uri']} {cmd}".split(" ")
  return subprocess.check_output(full_cmd).decode('utf-8')
