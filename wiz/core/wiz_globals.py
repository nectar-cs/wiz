
class WizGlobals:

  def __init__(self, ):
    self._concerns_base = None
    self._steps_base = None
    self.concerns_tree = {}

  @property
  def concerns_base(self):
    return self._concerns_base

  @concerns_base.setter
  def concerns_base(self, _module):
    self._concerns_base = _module.__name__

  @property
  def steps_base(self):
    return self._steps_base

  @steps_base.setter
  def steps_base(self, _module):
    self._steps_base = _module.__name__

wiz_globals = WizGlobals()