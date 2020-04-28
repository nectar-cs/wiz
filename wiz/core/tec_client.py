import subprocess
from typing import Tuple, Dict, List

import yaml

from k8_kat.res.config_map.kat_map import KatMap
from k8_kat.res.pod.kat_pod import KatPod
from wiz.core.res_match_rule import ResMatchRule
from wiz.core.types import K8sRes
from wiz.core.wiz_globals import wiz_globals

tec_pod_name = 'ted'
tmp_file_mame = '/tmp/man.yaml'
interpolate_cmd = "pipenv run python3 app.py kerbi interpolate"

def master_map():
  return KatMap.find(wiz_globals.ns, 'master')


def commit_values(assignments: [Tuple[str, any]]):
  existing_config = master_map().json('master')
  for assignment in assignments:
    fqhk_array = assignment[0].split('.')
    value = assignment[1]
    deep_set(existing_config, fqhk_array, value)
  master_map().set_json('master', master_map)


def apply(rules: List[ResMatchRule]):
  write_manifest(tmp_file_mame, rules)
  kubectl_apply(tmp_file_mame)


def gen_raw_manifest() -> List[K8sRes]:
  result = tec_pod().shell_exec(interpolate_cmd)
  return list(yaml.load_all(result, Loader=yaml.FullLoader))


def tec_pod():
  return KatPod.find(wiz_globals.ns, tec_pod_name)


def filter_res(res_list: List[K8sRes], rules: List[ResMatchRule]) -> List[K8sRes]:
  def decide_res(res):
    for rule in rules:
      if rule.evaluate(res):
        return True
    return False
  return [res for res in res_list if decide_res(res)]


def write_manifest(fname, rules: List[ResMatchRule]):
  all_res = gen_raw_manifest()
  filtered = filter_res(all_res, rules)
  composed = yaml.dump_all(filtered)
  with open(fname, 'w') as file:
    file.write(composed)


def kubectl_apply(fname):
  subprocess.check_output(
    f"kubectl apply -f {fname}"
  )


def deep_set(dict_root: Dict, names: List[str], value: any):
  if len(names) == 1:
    dict_root[names[0]] = value
  else:
    if not dict_root.get(names[0]):
      dict_root[names[0]] = dict()
    deep_set(dict_root[names[0]], names[1:], value)

