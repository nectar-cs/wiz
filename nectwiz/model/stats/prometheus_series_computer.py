from datetime import datetime

from nectwiz.core.core import prom_client
from nectwiz.model.stats.prometheus_computer import PrometheusComputer


class PrometheusSeriesComputer(PrometheusComputer):

  def compute(self):
    result = prom_client.compute_series(
      self.query_expr,
      self.step,
      self.t0,
      datetime.now()
    )
