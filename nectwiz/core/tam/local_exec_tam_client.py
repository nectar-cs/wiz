import subprocess
from typing import Dict, List

import yaml

from nectwiz.core.core.types import K8sResDict, TamDict

from nectwiz.core.tam.tam_client import TamClient

tmp_vars_path = '/tmp/necwiz-tmp-values.yaml'


class LocalExecTamClient(TamClient):
  def load_default_values(self) -> Dict[str, str]:
    raw = exec_cmd(self.tam, f"show values . {self.any_cmd_args()}")
    return yaml.load(raw, Loader=yaml.FullLoader)

  def template_manifest(self, values) -> List[K8sResDict]:
    write_values_to_tmpfile(values)
    cmd_args = self.template_cmd_args(tmp_vars_path)
    raw = exec_cmd(self.tam, f"template {cmd_args}")
    return list(yaml.load_all(raw, Loader=yaml.FullLoader))


def write_values_to_tmpfile(values: Dict):
  file_content = yaml.dump(values)
  with open(tmp_vars_path, 'w') as file:
    file.write(file_content)


def exec_cmd(tam: TamDict, cmd):
  uri, ver = tam['uri'], tam.get('version')
  exec_name = f"{uri}:{ver}" if ver else uri
  full_cmd = f"{exec_name} {cmd}".split(" ")
  output = subprocess.check_output(full_cmd).decode('utf-8')
  return output
