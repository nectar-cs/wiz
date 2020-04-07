
class StepState:
  pass

class Step:

  def __init__(self, step_state):
    self.state = step_state

  def apply(self):
    # for each of my fields, field.apply()
    # my_adapter.apply()
    pass

