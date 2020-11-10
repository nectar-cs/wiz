import traceback
from abc import ABC
from datetime import datetime, timedelta
from typing import Dict, Optional, List

from nectwiz.core.core import subs
from nectwiz.core.core.config_man import config_man
from nectwiz.model.stats.metrics_computer import MetricsComputer


class PrometheusComputer(MetricsComputer, ABC):
  def __init__(self, config: Dict):
    super().__init__(config)
    self.query_expr = inflate_query_expr(config.get('query'))
    self.step = config.get('step', '1h')
    self.t0 = parse_from_now(config.get('t0_offset', {'days': 7}))
    self.tn = parse_from_now(config.get('tn_offset', {}))

  @staticmethod
  def fetch_server_computed_result(raw) -> Optional[List]:
    if raw:
      try:
        return raw['data']['result']
      except KeyError:
        print(traceback.format_exc())
        print("[nectwiz:prometheus_computer] fmt err ^")
        return None
    else:
      return None


def inflate_query_expr(raw: str) -> str:
  substitutions = dict(resolvers=config_man.resolvers())
  interpolated: str = subs.interp(raw, substitutions)
  return interpolated.replace("<<", "{").replace(">>", "}")


def parse_from_now(expr: Dict) -> datetime:
  difference = {k: int(v) for k, v in expr.items()}
  return datetime.now() - timedelta(**difference)
