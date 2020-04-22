class StepState:

  def __init__(self, values_dict):
    self.values_dict = values_dict

  def value(self, name):
    return self.values_dict[name]