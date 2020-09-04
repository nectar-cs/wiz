from typing import List

from k8kat.res.base.kat_res import KatRes

from nectwiz.model.base.res_match_rule import ResMatchRule


def res_sel_to_res(root) -> List[KatRes]:
  """
  Selects resources that match the set of rules provided in root.
  :param root: polymorphic: string, eg "pod:*" or ["pod:*", "dep:*"]
  :return: list of KatRes resources.
  """
  root = [root] if not type(root) == list else root
  groups = [ResMatchRule(node).query() for node in root]
  return [item for sublist in groups for item in sublist]
