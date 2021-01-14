from datetime import datetime
from typing import List, Optional, Dict

import humanize
from werkzeug.utils import cached_property

from nectwiz.core.core.types import TimeSeriesDataPoint
from nectwiz.model.glance.glance import Glance
from nectwiz.model.humanizer.quantity_humanizer import QuantityHumanizer


class TimeSeriesGlance(Glance):

  DATA_KEY = 'time_series_data'
  REDUCER_FUNC_KEY = 'reducer'
  HUMANIZER_KEY = 'humanizer'
  IS_BIG_BETTER_KEY = 'big_means_better'

  @cached_property
  def view_type(self) -> str:
    return 'chart'

  @cached_property
  def info(self):
    if len(self.time_series) > 0:
      ts0 = self.time_series[0]['timestamp']
      delta_str = humanize.naturaltime(datetime.fromisoformat(ts0))
      return f"{delta_str} - now"
    else:
      return "Not enough data"

  @cached_property
  def time_series(self) -> List[TimeSeriesDataPoint]:
    return self.get_prop(self.DATA_KEY)

  @cached_property
  def reducer_type(self) -> str:
    return self.get_prop(self.REDUCER_FUNC_KEY, 'last')

  @cached_property
  def big_means_better(self) -> bool:
    return self.get_prop(self.IS_BIG_BETTER_KEY, True)

  @cached_property
  def humanizer(self) -> QuantityHumanizer:
    return self.inflate_child(
      QuantityHumanizer,
      prop=self.HUMANIZER_KEY,
      safely=True
    ) or QuantityHumanizer({})

  # noinspection PyBroadException
  def summary_quant(self) -> Optional[float]:
    try:
      if self.reducer_type == 'last':
        return _last_data_point(self.time_series)
      elif self.reducer_type == 'sum':
        return _series_sum(self.time_series)
    except:
      return None

  @cached_property
  def legend_icon(self) -> str:
    challenge = self.summary_quant() or 0
    is_greater = challenge > _series_avg(self.time_series)
    return "arrow_circle_up" if is_greater else "arrow_circle_down"

  @cached_property
  def legend_emotion(self) -> Optional[str]:
    if 'up' in self.legend_icon:
      return 'milGreen' if self.big_means_better else 'warning2'
    else:
      return 'warning2' if self.big_means_better else 'milGreen'

  def content_spec(self):
    series = [humanize_datapoint(d, self.humanizer) for d in self.time_series]
    return {
      'data': series,
      'value': self.humanizer.humanize_expr(self.summary_quant())
    }


def humanize_datapoint(datapoint, humanizer: QuantityHumanizer):
  return {
    **datapoint,
    'value': humanizer.humanize_quantity(datapoint['value'])
  }


def _last_data_point(series: List[Dict]) -> Optional[float]:
  if len(series) > 0:
    return series[len(series) - 1]['value']
  else:
    return None


def _series_sum(series: List[TimeSeriesDataPoint]) -> float:
  return sum([float(d['value'] or 0) for d in series])


def _series_avg(series: List[TimeSeriesDataPoint]) -> float:
  try:
    return _series_sum(series) / len(series)
  except ValueError:
    return 0.0
