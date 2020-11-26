from typing import Dict

from werkzeug.utils import cached_property

from nectwiz.model.stats.metrics_computer import MetricsComputer


class NumAndChartStatsProvider(MetricsComputer):

  VIEW_TYPE_KEY = 'view_type'
  NUMBER_COMPUTER_KEY = 'number'
  SERIES_COMPUTER_KEY = 'series'

  @cached_property
  def view_type(self) -> str:
    return self.get_prop(self.VIEW_TYPE_KEY)

  @cached_property
  def number_computer(self):
    return self.inflate_child(
      MetricsComputer,
      prop=self.NUMBER_COMPUTER_KEY,
      safely=True
    )

  @cached_property
  def series_computer(self):
    return self.inflate_child(
      MetricsComputer,
      prop=self.SERIES_COMPUTER_KEY,
      safely=True
    )

  def _do_compute(self):
    return {
      'number': self.number_computer,
      'series': self.series_computer
    }
