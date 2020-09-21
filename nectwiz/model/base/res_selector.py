from typing import List

from k8kat.res.base.kat_res import KatRes

from nectwiz.model.base.resource_selector import ResourceSelector


def to_reslist(root) -> List[KatRes]:
  """
  Selects resources that match the set of rules provided in root.
  :param root: polymorphic: string, eg "pod:*" or ["pod:*", "dep:*"]
  :return: list of KatRes resources.
  """
  root = [root] if not type(root) == list else root
  groups = [ResourceSelector(node).query() for node in root]
  return [item for sublist in groups for item in sublist]
