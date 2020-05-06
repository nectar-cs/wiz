import json
import os
import random
import string
import subprocess
from pathlib import Path
from typing import Dict

legal_envs = ['production', 'development', 'test']


def shell_exec(cmd) -> str:
  formatted_cmd = cmd.split(' ')
  output = subprocess.run(
    formatted_cmd,
    stdout=subprocess.PIPE
  )
  return output.stdout


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
    os.environ['KAT_ENV'] = _run_env
  else:
    raise Exception(f"Bad environment '{_run_env}'")


def run_env() -> str:
  return os.environ.get('FLASK_ENV', 'production')


def is_prod() -> bool:
  return run_env() == 'production'


def is_dev() -> bool:
  return run_env() == 'development'


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


def flatten(nested_list):
  return [item for sublist in nested_list for item in sublist]
