import subprocess
from typing import List, Tuple, Optional

import yaml
from k8kat.auth.kube_broker import broker

from nectwiz.core.core.types import K8sResDict
from nectwiz.model.base.res_match_rule import ResMatchRule

tmp_file_mame = '/tmp/man.yaml'

class TamClient:

  def load_manifest_defaults(self):
    raise NotImplemented

  def load_tpd_manifest(self, inlines=None) -> List[K8sResDict]:
    raise NotImplemented

  def apply(self, rules: Optional[List[ResMatchRule]], inlines=None) -> str:
    """
    Retrieves the manifest from Tami, writes its contents to a temporary local
    file (filtering resources by rules), and runs kubectl apply -f on it.
    :param rules: rules to filter the manifest, if any.
    :param inlines: inline values to be applied together with the manifest, if any.
    :return: any generated terminal output from kubectl apply.
    """
    res_dicts = self.load_tpd_manifest(inlines)
    save_manifest_as_tmp(res_dicts, rules)
    return kubectl_apply()


def save_manifest_as_tmp(res_dicts: List[K8sResDict], rules: List[ResMatchRule]):
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
  cmd = f"kubectl apply -f {tmp_file_mame}"

  if not broker.is_in_cluster_auth():
    if broker.connect_config.get('context'):
      cmd = f"{cmd} --context={broker.connect_config['context']}"

  print(f"Running {cmd}")
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
