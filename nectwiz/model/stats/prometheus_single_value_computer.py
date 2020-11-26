from nectwiz.core.core import prom_api_client
from nectwiz.model.stats.prometheus_computer import PrometheusComputer


class PrometheusScalarComputer(PrometheusComputer):

  def _do_compute(self):
    result = self.fetch_value()
    if result:
      return float(result[0]['value'][1])
    else:
      return None

  def fetch_value(self):
    raw = prom_api_client.compute_instant(self.query_expr, self.tn)
    return self.fetch_server_computed_result(raw)
