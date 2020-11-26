from typing import Optional, Dict

from k8kat.res.base.kat_res import KatRes
from werkzeug.utils import cached_property

from nectwiz.core.core.config_man import config_man
from nectwiz.core.core.types import ErrDict


class ErrCtx:
  def __init__(self, errdict: ErrDict):
    self._errdict: Dict = errdict

  @cached_property
  def selectable_properties(self) -> Dict:
    all_keys = self._errdict.keys()
    avoid_keys = ['uuid', 'resource']
    good_keys = list(set(all_keys) - set(avoid_keys))
    base_level = {k: self._errdict[k] for k in good_keys}
    extras_level = self._errdict.get('extras', {})
    return {**base_level, **extras_level}

  @cached_property
  def event_type(self):
    return self._errdict.get('event_type')

  @cached_property
  def kubernetes_resource(self) -> Optional[KatRes]:
    res_dict = self._errdict.get('resource')
    return self.extract_kat_res(res_dict) if res_dict else None

  @cached_property
  def resource_dict(self) -> Dict:
    if self.kubernetes_resource:
      return self.kubernetes_resource.raw
    else:
      return self._errdict.get('resource')

  @staticmethod
  def extract_kat_res(res_desc: Dict) -> Optional[KatRes]:
    kind, name = res_desc.get('kind'), res_desc.get('name')
    if kind and name:
      kat_model = KatRes.class_for(kind)
      return kat_model.find(name, config_man.ns()) if kat_model else None
    return None
