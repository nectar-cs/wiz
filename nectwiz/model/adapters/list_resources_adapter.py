from typing import Dict, List

from k8kat.res.base.kat_res import KatRes
from nectwiz.core.core.config_man import config_man

from nectwiz.model.base.wiz_model import WizModel


class ResourceQueryAdapter(WizModel):

  def __init__(self, config: Dict):
    super().__init__(config)
    self.category_resources = config.get('category_resources', [])

  def query_in_category(self, category: str) -> List[KatRes]:
    kind_names = self.category_resources.get(category, [])
    resource_reprs = []
    for kind_name in kind_names:
      kat_model = KatRes.class_for(kind_name)
      if kat_model:
        resource_reprs += kat_model.list(config_man.ns())
      else:
        print(f"[nectwiz::rqa] DANGER no kat for {kind_name}")
    return resource_reprs
