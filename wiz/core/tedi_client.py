import subprocess
import time
from typing import Tuple, Dict, List, Optional
from urllib.parse import quote

import yaml

from k8_kat.auth.kube_broker import broker
from k8_kat.res.config_map.kat_map import KatMap
from k8_kat.res.pod.kat_pod import KatPod
from wiz.core.res_match_rule import ResMatchRule
from wiz.core.types import K8sResDict
from wiz.core.wiz_globals import wiz_globals
from wiz.core import wiz_globals as wg

tmp_file_mame = '/tmp/man.yaml'
interpolate_cmd = "pipenv run python3 app.py kerbi interpolate"

def master_map() -> KatMap:
  return KatMap.find('master', wiz_globals.ns)


def commit_values(assignments: List[Tuple[str, any]]):
  config_map = master_map()
  existing_config = config_map.yget()
  for assignment in assignments:
    fqhk_array = assignment[0].split('.')
    value = assignment[1]
    deep_set(existing_config, fqhk_array, value)

  config_map.raw.data['master'] = yaml.dump(existing_config)
  config_map.touch(save=True)


def apply(rules: List[ResMatchRule], inlines=None):
  write_manifest(rules, inlines)
  kubectl_apply()


def fmt_inline_assigns(str_assignments: List[Tuple[str, any]]) -> str:
  expr_array = []
  for str_assignment in str_assignments:
    key_expr, value = str_assignment
    expr_array.append(f"--set {key_expr}:{value}")
  return " ".join(expr_array)


def load_raw_manifest(inlines=None) -> List[K8sResDict]:
  pod = tedi_pod()
  pod.trigger()
  vendor_flags: str = wiz_globals.app.get('te_args', '')
  inline_flags: str = fmt_inline_assigns(inlines or {})
  all_flags: str = f"{vendor_flags} {inline_flags}"
  command = f"{interpolate_cmd} --args [{quote(all_flags)}]"
  result = pod.shell_exec(command)
  return list(yaml.load_all(result, Loader=yaml.FullLoader))


def write_manifest(rules: List[ResMatchRule], inlines=None):
  all_res = load_raw_manifest(inlines)
  filtered = filter_res(all_res, rules)
  composed = yaml.dump_all(filtered)
  with open(tmp_file_mame, 'w') as file:
    file.write(composed)


def tedi_pod() -> Optional[KatPod]:
  if wiz_globals.ns:
    return KatPod.find(wg.tedi_pod_name, wiz_globals.ns)
  else:
    return None


def filter_res(res_list: List[K8sResDict], rules: List[ResMatchRule]) -> List[K8sResDict]:
  if rules:
    def decide_res(res):
      for rule in rules:
        if rule.evaluate(res):
          return True
      return False
    return [res for res in res_list if decide_res(res)]
  else:
    return res_list


def kubectl_apply():
  kubectl_bin = "kubectl"
  cmd = f"{kubectl_bin} apply -f {tmp_file_mame}"

  if not broker.is_in_cluster_auth():
    if broker.connect_config.get('context'):
      cmd = f"{cmd} --context={broker.connect_config['context']}"

  print("Running")
  return subprocess.check_output(cmd.split(" "))


def deep_set(dict_root: Dict, names: List[str], value: any):
  if len(names) == 1:
    dict_root[names[0]] = value
  else:
    if not dict_root.get(names[0]):
      dict_root[names[0]] = dict()
    deep_set(dict_root[names[0]], names[1:], value)
