from werkzeug.utils import cached_property

from nectwiz.model.humanizer.quantity_humanizer import QuantityHumanizer


class CoresHumanizer(QuantityHumanizer):

  @cached_property
  def suffix(self):
    return self.get_prop(self.SUFFIX_KEY, 'Cores')
