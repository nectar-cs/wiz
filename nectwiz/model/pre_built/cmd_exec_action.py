import subprocess
from typing import List

from nectwiz.core.core.types import ActionOutcome
from nectwiz.core.core.wiz_app import wiz_app
from nectwiz.model.action.action import Action


class CmdExecAction(Action):

  def __init__(self, config):
    super().__init__(config)
    self.cmd = config.get('cmd')

  def perform(self, **kwargs) -> ActionOutcome:
    final_cmd = interpolate_cmd(self.cmd, kwargs)
    result = subprocess.check_output(final_cmd.split(" "))
    out = result.decode('utf-8') if result else None
    logs = out.split("\n") if out else []

    return ActionOutcome(
      **self.outcome_template(),
      charge=result is not None,
      summary=f"{final_cmd} returned code ?",
      data=dict(output=out, logs=logs)
    )


def interpolate_cmd(cmd: str, buckets):
  words: List[str] = cmd.split(' ')
  return " ".join(list(map(interpolate_token, *[words, buckets])))


def interpolate_token(token: str, buckets) -> str:
  if token == '$app':
    return wiz_app.ns()
  elif token.startswith("$vars"):
    _, bucket_name, var_name = token.split("::")
    return buckets[bucket_name][var_name]
  else:
    return token
