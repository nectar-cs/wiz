from typing import List

from k8kat.res.base.kat_res import KatRes
from werkzeug.utils import cached_property

from nectwiz.core.core.config_man import config_man
from nectwiz.model.base.wiz_model import WizModel


class ResourceQueryAdapter(WizModel):

  CATEGORIES_KEY = 'category_resources'

  @cached_property
  def category_resources(self):
    return self.resolve_prop(self.CATEGORIES_KEY, backup={}, warn=True)

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
