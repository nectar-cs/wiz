import subprocess
from typing import Dict

from nectwiz.core.core import utils
from nectwiz.model.action.base.action import Action


class CmdExecAction(Action):

  def __init__(self, config):
    super().__init__(config)
    self.cmd = self.get_prop('cmd', '', {})

  def perform(self, **kwargs) -> Dict:
    result = subprocess.check_output(self.cmd.split(" "))
    logs = utils.clean_log_lines(result.decode('utf-8'))
    return dict(logs=logs)


def interpolate_token(token: str, buckets) -> str:
  from nectwiz.core.core.config_man import config_man
  if token == '$app':
    return config_man.ns()
  elif token.startswith("$vars"):
    _, bucket_name, var_name = token.split("::")
    return buckets[bucket_name][var_name]
  else:
    return token
