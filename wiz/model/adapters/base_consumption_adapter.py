from k8_kat.res.cluster.kat_cluster import KatCluster
from k8_kat.res.ns.kat_ns import KatNs
from wiz.core.wiz_globals import wiz_app
from wiz.model.adapters.adapter import Adapter


class BaseConsumptionAdapter(Adapter):

  def cluster_cpu(self):
    return KatCluster.cpu_capacity()

  def cluster_mem(self):
    return KatCluster.mem_capacity()

  def cpu_used(self):
    return KatNs.find(wiz_app.ns).cpu_used()

  def mem_used(self):
    return KatNs.find(wiz_app.ns).mem_used()

  def serialize(self, **kwargs):
    return dict(
      cluster_cpu=self.cluster_cpu(),
      cluster_mem=self.cluster_mem(),
      cpu_unit='Cores',
      cpu_used=self.cpu_used(),
      mem_used=self.mem_used(),
      mem_unit='Gb'
    )