from typing import Optional, Dict

from werkzeug.utils import cached_property

from nectwiz.model.glance.glance import Glance
from nectwiz.model.humanizer.quantity_humanizer import QuantityHumanizer


class PercentageGlance(Glance):

  PCT_KEY = 'pct'
  FRACTION_KEY = 'fraction'
  NUMERATOR_KEY = 'numerator'
  DENOMINATOR_KEY = 'denominator'
  ABS_HUMANIZER = 'parts_humanizer'
  PCT_HUMANIZER = 'pct_humanizer'

  @cached_property
  def abs_humanizer(self):
    return self.inflate_child(
      QuantityHumanizer,
      prop=self.ABS_HUMANIZER,
      safely=True
    ) or QuantityHumanizer({})

  @cached_property
  def info(self) -> str:
    humanize = lambda flt: self.abs_humanizer.humanize_expr(flt)
    to_s = lambda flt: humanize(flt) if flt is not None else 'N/A'
    return f"{to_s(self.numerator)} of {to_s(self.denominator)}"

  @cached_property
  def pct(self) -> float:
    return self.get_prop(self.PCT_KEY, self.fraction * 100)

  @cached_property
  def fraction(self) -> Optional[float]:
    return self.resolve_prop(
      self.FRACTION_KEY,
      lazy_backup=lambda: self.numerator / self.denominator
    )

  @cached_property
  def numerator(self) -> Optional[float]:
    return self.get_prop(self.NUMERATOR_KEY)

  @cached_property
  def denominator(self) -> Optional[float]:
    return self.get_prop(self.DENOMINATOR_KEY)

  @cached_property
  def pct_text(self) -> str:
    return f"{str(int(self.pct))}%"

  def content_spec(self) -> Dict:
    return {
      'pct': self.pct,
      'text': self.pct_text
    }
