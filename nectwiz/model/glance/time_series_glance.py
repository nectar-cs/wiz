import traceback
from typing import List, Optional, Dict

from werkzeug.utils import cached_property

from nectwiz.core.core.types import TimeSeriesDataPoint
from nectwiz.model.glance.glance import Glance
from nectwiz.model.humanizer.quantity_humanizer import QuantityHumanizer


class TimeSeriesGlance(Glance):

  DATA_KEY = 'time_series_data'
  REDUCER_FUNC_KEY = 'reducer'
  SERIES_VALUE_KEY_KEY = 'data_key'
  HUMANIZER_KEY = 'humanizer'

  @cached_property
  def view_type(self) -> str:
    return 'chart'

  @cached_property
  def time_series(self) -> List[TimeSeriesDataPoint]:
    return self.get_prop(self.DATA_KEY)

  @cached_property
  def reducer_type(self):
    return self.get_prop(self.REDUCER_FUNC_KEY, 'last')

  @cached_property
  def data_key(self) -> str:
    return self.get_prop(self.SERIES_VALUE_KEY_KEY, 'value')

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
      print(f"REDUCER TYPE {self.reducer_type}")
      if self.reducer_type == 'last':
        return _last_data_point(self.time_series, self.data_key)
      elif self.reducer_type == 'sum':
        return _series_sum(self.time_series)
    except:
      print(traceback.format_exc())
      return None

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


def _last_data_point(series: List[Dict], key: str) -> Optional[float]:
  print(f"Hey deciding {series}")
  if len(series) > 0:
    print(f"Last data point {series[len(series) - 1]}")
    return series[len(series) - 1][key]
  else:
    return None


def _series_sum(series: List[TimeSeriesDataPoint]) -> float:
  return sum([float(d['value'] or 0) for d in series])
