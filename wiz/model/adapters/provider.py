from typing import List, TypeVar, Generic

from wiz.model.adapters.adapter import Adapter

T = TypeVar('T', Adapter, Adapter)
class Provider(Generic[T]):

  def __init__(self, options=None):
    self.options = options or {}

  @classmethod
  def kind(cls) -> T:
    return T

  def produce_adapters(self) -> List[T]:
    raise NotImplementedError


