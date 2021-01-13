from werkzeug.utils import cached_property

from nectwiz.model.glance.glance import Glance


class BatteryGlance(Glance):

  @cached_property
  def view_type(self):
    return 'battery'

  def content_spec(self):
    pass
