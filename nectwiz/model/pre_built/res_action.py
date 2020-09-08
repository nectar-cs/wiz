import subprocess
from plistlib import Dict
from typing import List


from nectwiz.core.core.wiz_app import wiz_app


class ResAction:

  def __init__(self, config: Dict):
    self.cmd: str = config.get('cmd', '')

  def run(self):
    final_cmd = interpolate_cmd(self.cmd)
    result = subprocess.check_output(final_cmd.split(" "))
    return result.decode('utf-8') if result else None


def interpolate_cmd(cmd: str):
  words: List[str] = cmd.split(' ')
  return " ".join(list(map(interpolate_token, words)))


def interpolate_token(token):
  if token == '$app':
    return wiz_app.ns()
  else:
    return token
