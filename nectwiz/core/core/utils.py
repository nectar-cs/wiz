import functools
import json
import os
import random
import string
import subprocess
import sys
from collections.abc import Iterable
from functools import reduce
from os import listdir
from os.path import isfile, join
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

import yaml
from k8kat.auth.kube_broker import broker
from yaml import scanner

from nectwiz.core.core.types import KAO

legal_envs = ['production', 'development', 'test']


def exec_mode() -> str:
  from_argv = sys.argv[1] if len(sys.argv) >= 2 else None
  from_env = os.environ.get('WIZ_EXEC_MODE')
  return from_argv or from_env or 'server'


def is_in_cluster() -> bool:
  return broker.is_in_cluster_auth()


def is_out_of_cluster() -> bool:
  return not is_in_cluster()


def is_server() -> bool:
  return exec_mode() == 'server'


def is_worker() -> bool:
  return exec_mode() == 'worker'


def is_opsim() -> bool:
  return exec_mode() == 'opsim'


def is_shell() -> bool:
  return exec_mode() == 'shell'


def listlike(value: Any) -> bool:
  return isinstance(value, list)


def worker_uuid() -> Optional[str]:
  return os.environ.get('WIZ_WORKER_UUID')


def keyed2dict(keyed_assigns: List[Tuple[str, any]]) -> Dict:
  root = {}
  for keyed_assign in keyed_assigns:
    deep_key_as_list = keyed_assign[0].split('.')  # fully qualified hash key
    deep_set(root, deep_key_as_list, keyed_assign[1])
  return root


def flat2deep(flat_dict: Dict) -> Dict:
  return keyed2dict(list(flat_dict.items()))


def dict2keyed(assigns: Dict) -> List[Tuple[str, any]]:
  list_keyed_dict = _dict2keyed([], assigns)
  massager = lambda t: (".".join(t[0]), t[1])
  return list(map(massager, list_keyed_dict))


def dict2flat(assigns) -> Dict:
  tuples = dict2keyed(assigns)
  return {t[0]: t[1] for t in tuples}


def _dict2keyed(parents, assigns: Dict) -> List[Tuple[List[str], any]]:
  result: List[Tuple[List[str], any]] = []

  for assign in assigns.items():
    key, value = assign
    if type(value) == dict:
      result = result + _dict2keyed(parents + [key], value)
    else:
      result.append((parents + [key], value))
  return result


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


def deep_get2(dict_root: Dict, deep_key) -> Any:
  return deep_get(dict_root, deep_key.split('.'))


def deep_get(dict_root: Dict, keys: List[str]) -> Any:
  """
  Iterates over items in keys list, using them as keys to go deeper into the
  dictionary at each iteration. Eventually retrieves the value of the final key.
  :param dict_root: dict containing the desired value.
  :param keys: list of keys to be iterated over, to find the right depth.
  :return: value of the final key.
  """
  keys = [k for k in keys if not k.strip() == '']

  if len(keys) > 0:
    return reduce(
      lambda d, key: d.get(key, None)
      if isinstance(d, dict)
      else None, keys, dict_root
    )
  else:
    return dict_root


def getattr_deep(obj, attr):
  """
  Deep attribute supply.
  :param obj: Object from which to get the attribute.
  :param attr: attribute to get.
  :return: value of the attribute if found, else None.
  """
  def _getattr(_obj, _attr):
    returned = getattr(_obj, _attr)
    return returned() if callable(returned) else returned
  try:
    return functools.reduce(_getattr, [obj] + attr.split('.'))
  except AttributeError:
    return None


def shell_exec(unsplit_cmd: str) -> str:
  formatted_cmd = unsplit_cmd.split(' ')
  output = subprocess.run(
    formatted_cmd,
    stdout=subprocess.PIPE
  )
  return output.stdout.decode('utf-8')


def yamls_in_dir(dirpath) -> [Dict]:
  """
  Parses all YAMLs in the passed dirpath into a single list of dicts.
  :param dirpath: path where YAMLs are located.
  :return: list of dicts.
  """
  is_yaml = lambda path: isfile(path) and path.endswith(".yaml")
  fnames = [f for f in listdir(dirpath) if is_yaml(join(dirpath, f))]
  yaml_arrays = [yamls_in_file(f"{dirpath}/{fname}") for fname in fnames]
  return [item for sublist in yaml_arrays for item in sublist]


def yamls_in_file(fname) -> List[Dict]:
  """
  Converts a YAML file into a list of dicts.
  :param fname: YAML file.
  :return: list of dicts.
  """
  with open(fname, 'r') as stream:
    file_contents = stream.read()
    try:
      return list(yaml.full_load_all(file_contents))
    except scanner.ScannerError as e:
      print(f"[nectwiz::utils] YAML parse error @ {fname}")
      raise e


def jk_exec(cmd, **kwargs) -> Dict[str, any]:
  cmd = f"{kmd(cmd, **kwargs)} -o json"
  result = shell_exec(cmd)
  return json.loads(result)


def k_exec(cmd, **kwargs) -> str:
  cmd = kmd(cmd, **kwargs)
  return shell_exec(cmd)


def kmd(cmd: str, **kwargs) -> str:
  kubectl = kwargs.get('k', 'kubectl')
  ns = kwargs.get('ns', None)
  context = kwargs.get('ctx', None)

  cmd = f"{cmd} -n {ns}" if ns else cmd
  cmd = f"{cmd} --context={context}" if context else cmd
  cmd = f"{kubectl} {cmd}"

  return cmd


def root_path() -> str:
  return str(Path(__file__).parent.parent.parent)


def set_run_env(_run_env):
  if _run_env in legal_envs:
    os.environ['FLASK_ENV'] = _run_env
    os.environ['KAT_ENV'] = _run_env
  else:
    raise Exception(f"Bad environment '{_run_env}'")


def run_env() -> str:
  return os.environ.get('FLASK_ENV', 'production')


def is_prod() -> bool:
  return run_env() == 'production'


def is_dev() -> bool:
  return run_env() == 'development'


def is_in_cluster_dev():
  return is_dev() and broker.is_in_cluster_auth()


def is_local_dev_server():
  return not broker.is_in_cluster_auth()


def is_test() -> bool:
  return run_env() == 'test'


def is_ci() -> bool:
  return is_test() and os.environ.get('CI')


def is_ci_keep():
  return os.environ.get("CI") == 'keep'


def is_non_trivial(dict_array):
  if not dict_array:
    return False
  return [e for e in dict_array if e]


def is_either_hash_in_hash(big_hash, little_hashes):
  little_tuples = [list(h.items())[0] for h in little_hashes]
  for _tuple in (big_hash or {}).items():
    if _tuple in little_tuples:
      return True
  return False


# noinspection PyBroadException
def try_or(lam, fallback=None):
  try:
    return lam()
  except:
    return fallback


def dict_to_eq_str(_dict):
  return ",".join(
    ["=".join([k, str(v)]) for k, v in _dict.items()]
  )


def parse_dict_array(_string):
  parts = _string.split(',')
  return [parse_dict(part) for part in parts]


def parse_dict(encoded_dict):
  result_dict = {}
  for encoded_kv in encoded_dict.split(','):
    key, value = encoded_kv.split(':')
    result_dict[key] = value
  return result_dict


def rand_str(string_len=10):
  letters = string.ascii_lowercase
  return ''.join(random.choice(letters) for i in range(string_len))


def fqcn(o):
  module = o.__class__.__module__
  if module is None or module == str.__class__.__module__:
    return o.__class__.__name__
  else:
    return module + '.' + o.__class__.__name__


def coerce_cmd_format(cmd):
  if isinstance(cmd, str):
    return cmd.split(" ")
  else:
    return cmd


def clean_log_lines(chunk) -> List[str]:
  if type(chunk) == str:
    log_lines = chunk.split("\n")
    weeder = lambda line: not line.strip() == ''
    return list(filter(weeder, log_lines))
  elif type(chunk) == list:
    return chunk
  else:
    return []


def log2kao(log: str) -> Optional[KAO]:
  try:
    api = ''
    kind_and_name, verb = log.split(" ")
    kind, name = kind_and_name.split("/")
    if "." in kind:
      parts = kind.split(".")
      kind = parts[0]
      api = '.'.join(parts[1:])
    return KAO(
      api_group=api,
      kind=kind,
      name=name,
      verb=verb,
      error=None
    )
  except:
    return None


def kao2log(kao: KAO) -> str:
  group_and_kind = ''
  if kao.get('api_group'):
    group_and_kind = f"{kao.get('api_group')}."
  group_and_kind = f"{group_and_kind}{kao.get('kind')}"
  identity = f"{group_and_kind}/{kao.get('name')}"

  if not kao.get('error'):
    return f"{identity} {kao.get('verb')}"
  else:
    return f"{identity} {kao.get('error')}"


def logs2outkomes(logs: List[str]) -> List[KAO]:
  outcomes = list(map(log2kao, logs))
  return [o for o in outcomes if o is not None]


def flatten(nested_list):
  return [item for sublist in nested_list for item in sublist]


def unmuck_primitives(root: Any) -> Any:
  if type(root) == dict:
    return {k: unmuck_primitives(v) for k, v in root.items()}
  elif type(root) == list:
    return list(map(unmuck_primitives, root))
  else:
    return unmuck_primitive(root)


def isfloat(value):
  try:
    float(value)
    return True
  except ValueError:
    return False


def unmuck_primitive(original: Any) -> Any:
  if type(original) == str:
    if original.isdigit():
      return int(original)
    elif isfloat(original):
      return float(original)
    elif original.lower() == 'true':
      return True
    elif original.lower() == 'false':
      return False
    else:
      return original
  else:
    return original
