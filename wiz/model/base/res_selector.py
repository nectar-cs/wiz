from typing import List

from k8_kat.res.base.kat_res import KatRes

from wiz.model.base.res_match_rule import ResMatchRule


def res_sel_to_res(root) -> List[KatRes]:
  root = [root] if not type(root) == list else root
  groups = [ResMatchRule(node).query() for node in root]
  return [item for sublist in groups for item in sublist]
