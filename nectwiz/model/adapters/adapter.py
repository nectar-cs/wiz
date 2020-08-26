
class Adapter:

  def __init__(self, source=None):
    self.source = source or {}
    pass

  def serialize(self, **kwargs):
    return dict()
