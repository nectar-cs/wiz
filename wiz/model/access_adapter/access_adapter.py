

class AccessAdapter:

  @property
  def name(self):
    raise NotImplementedError

  def url(self):
    raise NotImplementedError

