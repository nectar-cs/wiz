from typing import Dict

from nectwiz.model.stats.metrics_computer import MetricsComputer


class NumAndChartStatsProvider(MetricsComputer):

  def __init__(self, config: Dict):
    super().__init__(config)
    self.view_type = config.get('view_type')
    self.number_computer_kod = config.get('number')
    self.series_computer_kod = config.get('series')

  def _do_compute(self):
    return {
      'number': self.compute_number(),
      'series': self.compute_series()
    }

  def compute_number(self):
    if self.number_computer_kod:
      self.load_child(MetricsComputer, self.number_computer_kod)

  def compute_series(self):
    if self.number_computer_kod:
      self.load_child(MetricsComputer, self.series_computer_kod)
