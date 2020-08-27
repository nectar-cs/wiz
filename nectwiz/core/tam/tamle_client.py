import subprocess

from nectwiz.core.tam.tam_client import TamClient


class TamleClient(TamClient):

  def exec_cmd(self):
    result = subprocess.check_output(cmd.split(" "))

  pass
