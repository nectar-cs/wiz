from typing import Dict, Optional, Any

from nectwiz.core.core.types import KoD
from nectwiz.model.stats.metrics_computer import MetricsComputer


class BasicResourceMetricsComputer(MetricsComputer):
  def __init__(self, config: Dict):
    super().__init__(config)
    cpu_conf, mem_conf = config.get('cpu', {}), config.get('memory', {})
    self.cpu_usage_now_computer_kod = cpu_conf.get('usage_now')
    self.mem_usage_now_computer_kod = mem_conf.get('usage_now')

    self.cpu_limit_now_computer_kod = cpu_conf.get('limit_now')
    self.mem_limit_now_computer_kod = mem_conf.get('limit_now')

    self.cpu_usage_series_computer_kod = cpu_conf.get('usage_series')
    self.mem_usage_series_computer_kod = mem_conf.get('usage_series')

  @classmethod
  def singleton_id(cls):
    return "nectar.metrics.mem-and-cpu-metrics-provider"

  def _do_compute(self):
    return dict(
      cpu_usage_now_cores=self.compute_cpu_usage_now_cores(),
      mem_usage_now_bytes=self.compute_mem_usage_now_bytes(),
      cpu_limit_now_cores=self.compute_cpu_limit_now_cores(),
      mem_limit_now_bytes=self.compute_mem_limit_now_bytes(),
      cpu_usage_series_cores=self.compute_cpu_usage_series_cores(),
      mem_usage_series_bytes=self.compute_mem_usage_series_bytes()
    )

  def compute_cpu_usage_now_cores(self):
    return self._compute_child(self.cpu_usage_now_computer_kod)

  def compute_mem_usage_now_bytes(self):
    return self._compute_child(self.mem_usage_now_computer_kod)

  def compute_cpu_limit_now_cores(self):
    return self._compute_child(self.cpu_limit_now_computer_kod)

  def compute_mem_limit_now_bytes(self):
    return self._compute_child(self.mem_limit_now_computer_kod)

  def compute_cpu_usage_series_cores(self):
    return self._compute_child(self.cpu_usage_series_computer_kod)

  def compute_mem_usage_series_bytes(self):
    return self._compute_child(self.mem_usage_series_computer_kod)

  def _compute_child(self, kod: KoD) -> Optional[Any]:
    if kod:
      computer = self.inflate_child(MetricsComputer, kod)
      computer.update_attrs(dict(step='1h', t0_offset=dict(days=1)))
      return computer.compute()
    else:
      return None
