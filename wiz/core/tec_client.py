import subprocess
from typing import Tuple, Dict, List

import yaml

from k8_kat.auth.kube_broker import broker
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
  config_map = master_map()
  existing_config = config_map.yaml('master')
  for assignment in assignments:
    fqhk_array = assignment[0].split('.')
    value = assignment[1]
    deep_set(existing_config, fqhk_array, value)

  config_map.raw.data['master'] = yaml.dump(existing_config)
  config_map.patch()


def apply(rules: List[ResMatchRule]):
  write_manifest(rules)
  kubectl_apply()


def load_raw_manifest() -> List[K8sRes]:
  pod = tec_pod()
  pod.trigger()
  result = pod.shell_exec(interpolate_cmd)
  return list(yaml.load_all(result, Loader=yaml.FullLoader))


def tec_pod():
  return KatPod.find(wiz_globals.ns, tec_pod_name)


def filter_res(res_list: List[K8sRes], rules: List[ResMatchRule]) -> List[K8sRes]:
  if rules:
    def decide_res(res):
      for rule in rules:
        if rule.evaluate(res):
          return True
      return False
    return [res for res in res_list if decide_res(res)]
  else:
    return res_list


def write_manifest(rules: List[ResMatchRule]):
  all_res = load_raw_manifest()
  filtered = filter_res(all_res, rules)
  composed = yaml.dump_all(filtered)
  with open(tmp_file_mame, 'w') as file:
    file.write(composed)


def kubectl_apply():
  kubectl_bin = "kubectl"
  cmd = f"{kubectl_bin} apply -f {tmp_file_mame} -n {wiz_globals.ns}"

  if not broker.is_in_cluster_auth():
    if broker.connect_config.get('context'):
      cmd = f"{cmd} --context={broker.connect_config['context']}"

  return subprocess.check_output(cmd.split(" "))


def deep_set(dict_root: Dict, names: List[str], value: any):
  if len(names) == 1:
    dict_root[names[0]] = value
  else:
    if not dict_root.get(names[0]):
      dict_root[names[0]] = dict()
    deep_set(dict_root[names[0]], names[1:], value)
