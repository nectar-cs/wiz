import os
import subprocess
import traceback
from typing import List, Optional, Dict

import yaml
from k8kat.auth.kube_broker import broker
from k8kat.utils.main.api_defs_man import api_defs_man
from typing_extensions import TypedDict

from nectwiz.core.core import utils
from nectwiz.core.core.config_man import config_man
from nectwiz.core.core.types import K8sResDict, TamDict, KAO
from nectwiz.model.base.resource_selector import ResourceSelector

tmp_file_mame = '/tmp/man.yaml'
ktl_apply_cmd_base = f"kubectl apply -f {tmp_file_mame}"
RESD = K8sResDict
RESDs = List[K8sResDict]
SELs = List[ResourceSelector]

class TamClientConstructorArgs(TypedDict):
  tam: TamDict


class TamClient:

  def __init__(self, **kwargs: TamClientConstructorArgs):
    self.tam: TamDict = kwargs.get('tam') or config_man.tam()

  def load_default_values(self):
    raise NotImplemented

  def template_manifest(self, values: Dict) -> List[K8sResDict]:
    raise NotImplemented

  def apply(self, **kwargs) -> List[KAO]:
    """
    Retrieves the manifest from Tami, writes its contents to a temporary local
    file (filtering resources by rules), and runs kubectl apply -f on it.
    :return: any generated terminal output from kubectl apply.
    """

    res_dicts = self.template_manifest(kwargs['values'])
    res_dicts = self.filter_res(res_dicts, kwargs.get('rules', []))
    return self.kubectl_apply(res_dicts)

  def any_cmd_args(self) -> str:
    return self.tam.get('args') or ''

  def template_cmd_args(self, inlines: Dict, vars_path: str) -> str:
    values_flag: str = f"-f {vars_path}"
    inline_flags: str = self.fmt_inline_assigns(inlines)
    ns = config_man.ns()
    return f"{ns} . {values_flag} {inline_flags} {self.any_cmd_args()}"

  @staticmethod
  def kubectl_apply(res_dicts: RESDs) -> List[KAO]:
    """
    Kubectl applies the manifest and returns any generated terminal output.
    :return: any generated teminal output.
    """
    outcomes: List[KAO] = []
    for res_dict in res_dicts:
      with short_lived_resfile(res_dict):
        command_parts = ktl_apply_cmd().split(" ")
        # noinspection PyBroadException
        try:
          result = subprocess.check_output(command_parts, stderr=subprocess.STDOUT)
          print(f"[nectwiz:tam_client] {command_parts} -----> {result}")
          outcomes.append(log2outcome(True, res_dict, result))
        except subprocess.CalledProcessError as e:
          print(traceback.format_exc())
          print(f"[nectwiz:tam_client] CalledProcessError {command_parts} ^^")
          outcomes.append(log2outcome(False, res_dict, e.output))
        except:
          print(traceback.format_exc())
          print(f"[nectwiz:tam_client] Unknown error {command_parts} ^^")
          outcomes.append(log2outcome(False, res_dict, traceback.format_exc()))
    return [o for o in outcomes if o]

  @staticmethod
  def filter_res(res_list: RESDs, selectors: SELs) -> RESDs:
    """
    Filters the list of parsed kubernetes resources from the tami-generated
    application manifest according to the passed rule-set.
    :param res_list: k8s resource list to be filtered.
    :param selectors: rules to be used for filtering.
    :return: filtered resource list.
    """
    def decide_res(res):
      for selector in selectors:
        if selector.selects_res(res):
          return True
      return False
    if selectors:
      return list(filter(decide_res, res_list))
    else:
      return res_list

  @staticmethod
  def fmt_inline_assigns(inlines: Dict) -> str:
    """
    Transforms in-memory assignments represented as tuples into a formatted
    assignment string following the --set = format usable for Tami's command line
    arguments.
    :param inlines: desired inline assigns.
    :return: command for the Tami image to apply inline assigns.
    """
    expr_array = []
    for key_expr, value in list((inlines or {}).items()):
      if not type(value) in [dict, list]:
        expr_array.append(f"--set {key_expr}={value}")
      else:
        print(f"[nectwiz:tam_client] non-primitive {key_expr} -> {value}")
    return " ".join(expr_array)

  @staticmethod
  def release_name():
    return config_man.ns()


def log2outcome(succs: bool, resdict: RESD, output) -> Optional[KAO]:
  raw_log = output.decode('utf-8') if output else ''
  parts = raw_log.split("\n")
  raw_log = parts[0] if len(parts) == 2 else None

  if raw_log:
    if succs:
      return utils.log2kao(raw_log)
    else:
      kind = resdict.get('kind')
      kind = api_defs_man.kind2plurname(kind) or kind
      api_group = api_defs_man.find_api_group(kind)
      return KAO(
        api_group=api_group,
        kind=kind,
        name=resdict.get('metadata', {}).get('name'),
        verb=None,
        error=raw_log
      )
  else:
    print(f"[nectwiz::tam_client] panic log fmt unknown: {raw_log}")
    return None


class short_lived_resfile:
  def __init__(self, resdict: K8sResDict):
    self.res_dict = resdict

  def __enter__(self):
    with open(tmp_file_mame, 'w') as file:
      file.write(yaml.dump(self.res_dict))

  def __exit__(self, exc_type, exc_val, exc_tb):
    if os.path.isfile(tmp_file_mame):
      if utils.is_prod():
        os.remove(tmp_file_mame)


def ktl_apply_cmd() -> str:
  final_cmd = ktl_apply_cmd_base
  if utils.is_out_of_cluster():
    if broker.connect_config.get('context'):
      context_part = f"--context={broker.connect_config['context']}"
      final_cmd = f"{final_cmd} {context_part}"
  return final_cmd
