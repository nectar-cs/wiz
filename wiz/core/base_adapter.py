
class BaseAdapter:

  def as_hash(self):
    raise NotImplementedError

  def commit(self):
    pass
