import subprocess
from typing import Dict, List

import yaml

from nectwiz.core.core.types import K8sResDict, TamDict
from nectwiz.core.core.config_man import config_man

from nectwiz.core.tam.tam_client import TamClient, gen_template_args

tmp_vars_path = '/tmp/necwiz-tmp-values.yaml'


class TamleClient(TamClient):
  def load_manifest_defaults(self) -> Dict[str, str]:
    raw = exec_cmd(self.tam, 'values')
    return yaml.load(raw, Loader=yaml.FullLoader)

  def load_templated_manifest(self, inlines=None) -> List[K8sResDict]:
    write_values_to_tmpfile()
    split_flags = gen_template_args(inlines, tmp_vars_path)
    flat_flags = " ".join(split_flags)
    raw = exec_cmd(self.tam, f'template {flat_flags}')
    return list(yaml.load_all(raw, Loader=yaml.FullLoader))


def write_values_to_tmpfile():
  file_content = yaml.dump(config_man.manifest_vars())
  with open(tmp_vars_path, 'w') as file:
    file.write(file_content)


def exec_cmd(tam: TamDict, cmd):
  uri, ver = tam['uri'], tam['version']
  exec_name = f"{uri}:{ver}" if ver else uri
  full_cmd = f"{exec_name} {cmd}".split(" ")
  output = subprocess.check_output(full_cmd).decode('utf-8')
  return output
