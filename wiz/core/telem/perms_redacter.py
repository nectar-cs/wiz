from typing import Dict, Optional, Union, List

from wiz.core.telem.serial import ApiOperationOutcome
from wiz.core.telem.sharing_perms import SharingPerms


def if_allowed(perms: SharingPerms, prop_name: str, value) -> Optional:
  can_share = perms.can_share_prop(prop_name)
  if can_share:
    return value() if callable(value) else value
  return None


def sanitize(perms, prefix, dirty_dict: Union[Dict, List]) -> Dict:
  new_dict = {}
  for key, value in dirty_dict:
    if type(value) == list:
      sub_key = f'{prefix}{key}.'
      child_sanitizer = lambda itm: sanitize(perms, sub_key, itm)
      comp_children = lambda: list(map(child_sanitizer, value))
      new_dict[key] = if_allowed(perms, key, comp_children)
    elif type(value) == dict:
      new_dict[key] = sanitize(perms, f'{prefix}{key}.', value)
    else:
      new_dict[key] = if_allowed(perms, f"{prefix}{key}", value)
  return new_dict


def redact(op_outcome: ApiOperationOutcome) -> ApiOperationOutcome:
  perms = SharingPerms()
  return sanitize(perms, 'operation_outcome', op_outcome)

