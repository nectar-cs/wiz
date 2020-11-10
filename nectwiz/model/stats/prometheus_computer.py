from datetime import datetime, timedelta
from typing import Dict

from nectwiz.core.core import prom_client
from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.stats.metrics_computer import MetricsComputer


class PrometheusComputer(MetricsComputer):
  def __init__(self, config: Dict):
    super().__init__(config)
    self._type = config.get('type', 'series')
    self.query_expr = config.get('query')
    self.step = config.get('step')
    self.t0 = parse_from_now(config.get('t0_offset', {'days': 7}))

  def compute(self):
    if self._type == 'series':
     result = prom_client.compute_series(
       self.query_expr,
       self.step,
       self.t0,
       datetime.now()
     )
    elif self._type == 'instant':
      result = prom_client.compute_instant(
        self.query_expr,
        self.t0
      )
    else:
      print(f"[nectwiz:prom_adapter] illegal type {self._type}")
      return None

    if result:
      pass
    else:
      print(f"[nectwiz:prom_adapter] illegal type {self._type}")


# def conv_series_point(point) -> Dict:


def parse_from_now(expr: Dict) -> datetime:
  difference = {k: int(v) for k, v in expr.items()}
  return datetime.now() - timedelta(**difference)
