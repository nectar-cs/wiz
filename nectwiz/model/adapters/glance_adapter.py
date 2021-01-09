from functools import cached_property

from nectwiz.model.base.wiz_model import WizModel


class GlanceAdapter(WizModel):

  TYPE_KEY = 'type'
  COLORS_KEY = 'colors'
  MIN_KEY = 'min'
  MAX_KEY = 'max'
  AS_PCT_KEY = 'as_pct_key'

  @cached_property
  def _type(self):
    return self.get_prop(self.TYPE_KEY)

  @cached_property
  def colors(self):
    return self.get_prop(self.COLORS_KEY)

  @cached_property
  def colors(self):
    return self.get_prop(self.COLORS_KEY)
