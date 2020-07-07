from functools import cached_property
from typing import Dict, Optional

from wiz.core import tedi_client, utils


class SharingPerms:

  @cached_property
  def user_perms(self) -> Dict:
    kat_map = tedi_client.master_cmap()
    return kat_map.jget('sharing_prefs', {}) if kat_map else {}

  def can_share_prop(self, prop: str) -> bool:
    if not utils.is_dev():
      category = prop_category(prop)
      if category:
        return self.user_perms.get(category)
      else:
        print(f"DANGER unaffiliated sharing prop {prop}")
        return False
    else:
      return True


def prop_category(prop) -> Optional[str]:
  for category in category_props_mapping:
    if prop in category:
      return category
  return None


category_props_mapping = {
  'operations.something': [

  ]
}