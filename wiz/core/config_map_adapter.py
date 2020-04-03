from typing import List, Tuple

from wiz.core.base_adapter import BaseAdapter


class KubectlWriteAdapter:

  def apply_file(self, url, res_ids: List[Tuple]):
    pass

class K8KatWriteAdapter:

  def create_from(self):
    pass

class ConfigMapAdapter(BaseAdapter):

  def as_hash(self):
    pass

  def commit(self):
    pass

  def cluster_commit(self):
    pass