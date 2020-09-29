import subprocess
from typing import List, Tuple, Optional

import yaml
from k8kat.auth.kube_broker import broker

from nectwiz.core.core.config_man import config_man
from nectwiz.core.core.types import K8sResDict, TamDict
from nectwiz.model.base.resource_selector import ResourceSelector

tmp_file_mame = '/tmp/man.yaml'

class TamClient:

  def __init__(self, tam: TamDict):
    self.tam: TamDict = tam

  def load_manifest_defaults(self):
    raise NotImplemented

  def load_templated_manifest(self, inlines=None) -> List[K8sResDict]:
    raise NotImplemented

  def apply(self, rules: Optional[List[ResourceSelector]], inlines=None) -> str:
    """
    Retrieves the manifest from Tami, writes its contents to a temporary local
    file (filtering resources by rules), and runs kubectl apply -f on it.
    :param rules: rules to filter the manifest, if any.
    :param inlines: inline values to be applied together with the manifest, if any.
    :return: any generated terminal output from kubectl apply.
    """
    res_dicts = self.load_templated_manifest(inlines)
    save_manifest_as_tmp(res_dicts, rules)
    return kubectl_apply()


def save_manifest_as_tmp(res_dicts: List[K8sResDict], rules: List[ResourceSelector]):
  """
  Launches Tami container with passed inline arguments. Then collects logs from
  resources that match the rules, and writes them out to a file.
  :param res_dicts: dict representation of resources
  :param rules: rules to be used for filtering resources.
  """
  filtered = filter_res(res_dicts, rules)
  composed = yaml.dump_all(filtered)
  with open(tmp_file_mame, 'w') as file:
    file.write(composed)


def kubectl_apply() -> str:
  """
  Kubectl applies the manifest and returns any generated terminal output.
  :return: any generated teminal output.
  """

  with open(tmp_file_mame, 'r') as file:
    as_dicts = yaml.load_all(file.read(), Loader=yaml.FullLoader)
    if len(list(as_dicts)) < 1:
      print("[nectwiz::tam_client] manifest empty, skipping kubectl apply")
      return ""

  cmd = f"kubectl apply -f {tmp_file_mame}"

  if not broker.is_in_cluster_auth():
    if broker.connect_config.get('context'):
      cmd = f"{cmd} --context={broker.connect_config['context']}"

  result = subprocess.check_output(cmd.split(" "))
  return result.decode('utf-8') if result else None


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


def filter_res(res_list: List[K8sResDict], selector: List[ResourceSelector]) -> List[K8sResDict]:
  """
  Filters the list of parsed kubernetes resources from the tami-generated
  application manifest according to the passed rule-set.
  :param res_list: k8s resource list to be filtered.
  :param selector: rules to be used for filtering.
  :return: filtered resource list.
  """
  if selector:
    def decide_res(res):
      for rule in selector:
        if rule.selects_res(res, {}):
          return True
      return False
    return [res for res in res_list if decide_res(res)]
  else:
    return res_list


def gen_template_args(inline_assigns, vars_full_path) -> List[str]:
  """
  Generates arguments to pass to the Tami image at startup.
  :param inline_assigns: desired inline assigns.
  :param vars_full_path: pointer to values file
  :return: list of flags to pass to Tami image.
  """
  default_inlines = [('namespace', config_man.ns())]
  inlines = default_inlines + (inline_assigns or [])
  values_flag: str = f"-f {vars_full_path}"
  vendor_flags: str = config_man.tam().get('args')
  inline_flags: str = fmt_inline_assigns(inlines)
  all_flags: str = f"{values_flag} {inline_flags} {vendor_flags}"
  return [w for w in all_flags.split(" ") if w]


