from functools import lru_cache
from typing import Optional, Dict

from k8kat.res.base.kat_res import KatRes

from nectwiz.core.core.config_man import config_man
from nectwiz.core.core.types import ErrDict


class ErrCtx:
  def __init__(self, errdict: ErrDict):
    self._errdict: ErrDict = errdict

  @lru_cache(maxsize=1)
  def selectable_properties(self) -> Dict:
    all_keys = self._errdict.keys()
    avoid_keys = ['uuid', 'resource']
    good_keys = list(set(all_keys) - set(avoid_keys))
    return {k: self._errdict[k] for k in good_keys}

  @lru_cache(maxsize=1)
  def event_type(self):
    return self._errdict.get('event_type')

  @lru_cache(maxsize=1)
  def resolve_resource(self) -> Optional[KatRes]:
    res_dict = self._errdict.get('resource')
    return self.extract_kat_res(res_dict) if res_dict else None

  def resource_dict(self) -> Dict:
    if self.resolve_resource():
      return self.resolve_resource().raw
    else:
      return self._errdict.get('resource')

  @staticmethod
  def extract_kat_res(res_desc: Dict) -> Optional[KatRes]:
    kind, name = res_desc.get('kind'), res_desc.get('name')
    if kind and name:
      kat_model = KatRes.class_for(kind)
      return kat_model.find(name, config_man.ns()) if kat_model else None
    return None
