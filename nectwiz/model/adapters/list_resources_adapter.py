from typing import Dict, List

from k8kat.res.base.kat_res import KatRes

from nectwiz.core.core.config_man import config_man
from nectwiz.model.base.wiz_model import WizModel


class ListResourcesAdapter(WizModel):

  def __init__(self, config: Dict):
    super().__init__(config)
    self.kind_names = config.get('resource_kinds', [])

  def list_resources(self) -> List[Dict]:
    resources = []
    for kind in self.kind_names:
      model: KatRes = KatRes.class_for(kind, None)
      kind_resources = model.list(config_man.ns())
      as_dicts = [res.raw for res in kind_resources]
      resources = resources + as_dicts
    return resources
