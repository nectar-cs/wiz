from typing import Dict, Optional, List

from k8kat.res.pod.kat_pod import KatPod
from k8kat.res.pvc.kat_pvc import KatPvc
from k8kat.utils.main.units import parse_quant_expr
from kubernetes.client import V1PersistentVolumeClaim

from nectwiz.core.core.config_man import config_man
from nectwiz.model.adapters.store_adapter import StoreAdapter
from nectwiz.model.base.resource_selector import ResourceSelector


class PvcStoreAdapter(StoreAdapter):
  def __init__(self, config: Dict):
    super().__init__(config)
    self.df_pod_selector: ResourceSelector = config.get('df_pod_selector')
    self.volume_path: str = config.get('volume_path')
    self.pvc_name: str = config.get('pvc_name')

  def capacity_bytes(self) -> Optional[int]:
    pvc = KatPvc.find(self.pvc_name, config_man.ns())
    if pvc:
      pvc_body: V1PersistentVolumeClaim = pvc.raw
      cap_expr = pvc_body.status.capacity.storage
      return int(parse_quant_expr(cap_expr)) if cap_expr else None

  def used_bytes(self) -> Optional[int]:
    pod = self.suitable_df_pod()
    if pod:
      raw_out = pod.shell_exec("df")
      df_rows = dfstr2rows(raw_out)
      find_vol = lambda r: r['Mount'] == self.volume_path
      target_row = next(filter(find_vol, df_rows), None)
      return int(target_row['Used']) if target_row else None

  def suitable_df_pod(self) -> Optional[KatPod]:
    if self.df_pod_selector:
      context = dict(resolvers=config_man.resolvers())
      query = self.df_pod_selector.query_cluster(context)
      return query[0] if len(query) > 0 else None
    else:
      return None

def dfstr2rows(table_str: str) -> List[Dict]:
  table_str = table_str.replace("Mounted on", 'Mount')
  lines = table_str.split("\n")
  headers = lines[0].strip().split(" ")
  rows = []
  for line in lines[1:]:
    cells = line.strip().split(' ')
    rows.append({headers[i]: cells[i] for i in range(len(headers))})
  return rows
