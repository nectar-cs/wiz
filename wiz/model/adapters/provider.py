from typing import List

from wiz.model.adapters.adapter import Adapter


class Provider:

  def __init__(self, options=None):
    self.options = options or {}

  def list(self) -> List[Adapter]:
    raise NotImplementedError
