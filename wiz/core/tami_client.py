import subprocess
from functools import reduce
from typing import Tuple, Dict, List, Optional

import yaml

from k8_kat.auth.kube_broker import broker
from k8_kat.res.config_map.kat_map import KatMap
from wiz.model.base.res_match_rule import ResMatchRule
from wiz.core.types import K8sResDict
from wiz.core.wiz_app import wiz_app
from wiz.core import tami_prep

tmp_file_mame = '/tmp/man.yaml'
interpolate_cmd = "pipenv run python3 app.py kerbi interpolate"
tami_name_key = 'tami_name'


def master_cmap() -> KatMap:
  """
  Returns the ConfigMap.
  :return: ConfigMap.
  """
  return KatMap.find('master', wiz_app.ns)


def commit_values(assignments: List[Tuple[str, any]]):
  """
  Updates the ConfigMap with the new assignments. Saves it.
  :param assignments: assigns to be inserted.
  """
  config_map = master_cmap()
  existing_config = config_map.yget() #parse yaml
  for assignment in assignments:
    fqhk_array = assignment[0].split('.')  # fully qualified hash key
    value = assignment[1]
    deep_set(existing_config, fqhk_array, value)

  config_map.raw.data['master'] = yaml.dump(existing_config) #make yaml
  config_map.touch(save=True)


def update_tami_name(new_name: str):
  config_map = master_cmap()
  config_map.kv_set(tami_name_key, new_name)


def read_tami_name():
  config_map = master_cmap()
  config_map.data.get(tami_name_key)


def chart_dump() -> Dict:
  """
  Parses the ConfigMap from YAML to a dict.
  :return: ConfigMap in dict form.
  """
  config_map = master_cmap()
  return config_map.yget() if config_map else {}


def chart_value(deep_key: str) -> Optional[str]:
  """
  Deep-gets the value specified as deep_key from the ConfigMap.
  :param deep_key: key in the following format: level1.level2.level3, where levels
  refer to keys at various depths of the dict, from most shallow to deepest.
  :return: value behind deep key.
  """
  return deep_get(chart_dump(), deep_key.split('.'))


def apply(rules: Optional[List[ResMatchRule]], inlines=None) -> str:
  """
  Retrieves the manifest from Tami, writes its contents to a temporary local
  file (filtering resources by rules), and runs kubectl apply -f on it.
  :param rules: rules to filter the manifest, if any.
  :param inlines: inline values to be applied together with the manifest, if any.
  :return: any generated terminal output from kubectl apply.
  """
  write_manifest(rules, inlines)
  return kubectl_apply()


def fmt_inline_assigns(str_assignments: List[Tuple[str, any]]) -> str:
  """
  Transforms in-memory assignments represented as tuples into a formatted
  assignment string following the --set = format usable for Tami's command line
  arguments.
  :param str_assignments: desired inline assigns.
  :return: command for the Tami image to apply inline assigns.
  """
  expr_array = []
  for str_assignment in str_assignments:
    key_expr, value = str_assignment
    expr_array.append(f"--set {key_expr}={value}")
  return " ".join(expr_array)


def gen_tami_args(inlines) -> List[str]:
  """
  Generates arguments to pass to the Tami image at startup.
  :param inlines: desired inline assigns.
  :return: list of flags to pass to Tami image.
  """
  values_flag: str = "-f /values/master"
  vendor_flags: str = wiz_app.tami_args
  inline_flags: str = fmt_inline_assigns(inlines or {})
  all_flags: str = f"{values_flag} {inline_flags} {vendor_flags}"
  return all_flags.split(" ")


def load_raw_manifest(inlines=None) -> List[K8sResDict]:
  """
  Creates a Kubernetes pod running the vendor-specified image, then reads the
  output logs, expected to be a string literal of the interpolated application manifest.
  :param inlines:
  :return: parsed logs from the Tami container.
  """
  ns, image_name = wiz_app.ns, wiz_app.tami_name
  pod_args = gen_tami_args(inlines)
  print(f"THE POD ARGS SHALL BE FROM {inlines}")
  print(pod_args)
  result = tami_prep.consume(ns, image_name, pod_args)
  return list(yaml.load_all(result, Loader=yaml.FullLoader))


def write_manifest(rules: List[ResMatchRule], inlines=None):
  """
  Launches Tami container with passed inline arguments. Then collects logs from
  resources that match the rules, and writes them out to a file.
  :param rules: rules to be used for filtering resources.
  :param inlines: inline arguments to be passed to the Tami container.
  """
  all_res = load_raw_manifest(inlines)
  filtered = filter_res(all_res, rules)
  composed = yaml.dump_all(filtered)
  with open(tmp_file_mame, 'w') as file:
    file.write(composed)


def filter_res(res_list: List[K8sResDict], rules: List[ResMatchRule]) -> List[K8sResDict]:
  """
  Filters the list of parsed kubernetes resources from the tami-generated
  application manifest according to the passed rule-set.
  :param res_list: k8s resource list to be filtered.
  :param rules: rules to be used for filtering.
  :return: filtered resource list.
  """
  if rules:
    def decide_res(res):
      for rule in rules:
        if rule.evaluate(res):
          return True
      return False
    return [res for res in res_list if decide_res(res)]
  else:
    return res_list


def kubectl_apply() -> str:
  """
  Kubectl applies the manifest and returns any generated terminal output.
  :return: any generated teminal output.
  """
  kubectl_bin = "kubectl"
  cmd = f"{kubectl_bin} apply -f {tmp_file_mame}"

  if not broker.is_in_cluster_auth():
    if broker.connect_config.get('context'):
      cmd = f"{cmd} --context={broker.connect_config['context']}"

  with open(tmp_file_mame, 'r') as file:
    print(file.read())

  print(f"Running {cmd}")
  result = subprocess.check_output(cmd.split(" "))
  print(result)
  return result.decode('utf-8') if result else None


def deep_set(dict_root: Dict, names: List[str], value: any):
  """
  Iterates over items in names list, using them as keys to go deeper into the
  dictionary at each iteration. Eventually sets the passed value with the final key.
  with the passed value.
  :param dict_root: dict to be modified with the desired value.
  :param names: list of names to be iterated over, to find the right depth.
  :param value: value to be eventually set at the right depth.
  """
  if len(names) == 1:
    dict_root[names[0]] = value
  else:
    if not dict_root.get(names[0]):
      dict_root[names[0]] = dict()
    deep_set(dict_root[names[0]], names[1:], value)


def deep_get(dict_root: Dict, keys: List[str]) -> str:
  """
  Iterates over items in keys list, using them as keys to go deeper into the
  dictionary at each iteration. Eventually retrieves the value of the final key.
  :param dict_root: dict containing the desired value.
  :param keys: list of keys to be iterated over, to find the right depth.
  :return: value of the final key.
  """
  return reduce(
    lambda d, key: d.get(key, None)
    if isinstance(d, dict)
    else None, keys, dict_root
  )
