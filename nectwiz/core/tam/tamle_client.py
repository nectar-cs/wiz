import subprocess
from typing import Dict

import yaml

from nectwiz.core.wiz_app import wiz_app

from nectwiz.core.tam.tam_client import TamClient


class TamleClient(TamClient):

  def load_manifest_defaults(self) -> Dict[str, str]:
    raw = exec_cmd('values')
    return yaml.load(raw, Loader=yaml.FullLoader)


def exec_cmd(cmd):
  full_cmd = f"{wiz_app.tam()['uri']} {cmd}".split(" ")
  return subprocess.check_output(full_cmd).decode('utf-8')
