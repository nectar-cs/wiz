import traceback
from abc import ABC
from datetime import datetime, timedelta
from typing import Dict, Optional, List

from werkzeug.utils import cached_property

from nectwiz.core.core import subs
from nectwiz.core.core.config_man import config_man
from nectwiz.model.supply.value_supplier import ValueSupplier


class PrometheusSupplier(ValueSupplier, ABC):

  QUERY_EXPR_KEY = 'query'
  STEP_KEY = 'step'
  T0_OFFSET_KEY = 't0_offset'
  TN_OFFSET_KEY = 'tn_offset'

  @cached_property
  def query_expr(self) -> str:
    return inflate_query_expr(self.get_prop(self.QUERY_EXPR_KEY))

  @cached_property
  def step(self) -> str:
    return self.get_prop(self.STEP_KEY, '1h')

  @cached_property
  def t0(self) -> datetime:
    offset = self.get_prop(self.T0_OFFSET_KEY, {'days': 7})
    return parse_from_now(offset)

  @cached_property
  def tn(self) -> datetime:
    offset = self.get_prop(self.TN_OFFSET_KEY, {})
    return parse_from_now(offset)

  @staticmethod
  def extract_datapoints(response: Dict) -> Optional[List]:
    if response:
      try:
        return response['data']['result']
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
