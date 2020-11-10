from typing import Dict

from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.stats.metrics_computer import MetricsComputer


class MemCpuStatsProvider(WizModel):

  def __init__(self, config: Dict):
    super().__init__(config)
    self.cpu_usage_now_computer_kod = config.get('cpu_usage_now')
    self.mem_usage_now_computer_kod = config.get('mem_usage_now')

    self.mem_limit_now_computer_kod = config.get('mem_limit_now')
    self.cpu_limit_now_computer_kod = config.get('cpu_limit_now')

    self.cpu_usage_series_computer_kod = config.get('cpu_usage_series')
    self.mem_usage_series_computer_kod = config.get('mem_usage_series')

  def compute_cpu_usage_now_milli_cores(self):
    if self.cpu_limit_now_computer_kod:
      self.load_child(MetricsComputer, self.cpu_limit_now_computer_kod)

  def compute_cpu_limit_now_milli_cores(self):
    pass