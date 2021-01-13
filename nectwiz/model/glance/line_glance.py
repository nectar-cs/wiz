from typing import List, Optional

from werkzeug.utils import cached_property

from nectwiz.core.core.types import TimeSeriesDataPoint
from nectwiz.model.glance.glance import Glance


class LineGlance(Glance):

  DATA_KEY = 'data'
  REDUCER_FUNC_KEY = 'reducer'
  ROUNDING_KEY = 'rounding'
  PREFIX_KEY = 'prefix'
  SUFFIX_KEY = 'suffix'

  @cached_property
  def line_data(self) -> List[TimeSeriesDataPoint]:
    return self.get_prop(self.DATA_KEY)

  @cached_property
  def reducer_type(self):
    return self.get_prop(self.DATA_KEY, 'last')

  @cached_property
  def rounding(self):
    return self.get_prop(self.ROUNDING_KEY, 1)

  @cached_property
  def prefix(self):
    return self.get_prop(self.PREFIX_KEY)

  @cached_property
  def suffix(self):
    return self.get_prop(self.SUFFIX_KEY)

  # noinspection PyBroadException
  def compute_final_point(self) -> Optional[float]:
    try:
      if self.reducer_type == 'last':
        return self.line_data[len(self.line_data) - 1]['value']
      elif self.reducer_type == 'sum':
        return sum([d['value'] for d in self.line_data])
    except:
      return None

  def content_spec(self):
    return {
      'data': self.line_data,
      'value': self.compute_final_point()
    }

