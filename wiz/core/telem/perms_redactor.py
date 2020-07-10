from typing import Dict, Optional, Union, List

from wiz.core.telem.serial import ApiOperationOutcome
from wiz.core.telem.sharing_perms import SharingPerms


def if_allowed(perms: SharingPerms, prop_name: str, value) -> Optional:
  can_share = perms.can_share_prop(prop_name)
  if can_share:
    return value() if callable(value) else value
  return None


def redact_for_perms(perms, prefix, dirty_dict: Union[Dict, List]) -> Dict:
  new_dict = {}
  for key, value in dirty_dict.items():
    full_key, sub_key = f'{prefix}{key}', f'{prefix}{key}.'
    if type(value) == list:
      child_sanitizer = lambda itm: redact_for_perms(perms, sub_key, itm)
      comp_children = lambda: list(map(child_sanitizer, value))
      new_dict[key] = if_allowed(perms, full_key, comp_children)
    elif type(value) == dict:
      comp = lambda: redact_for_perms(perms, sub_key, value)
      new_dict[key] = if_allowed(perms, full_key, comp)
    else:
      new_dict[key] = if_allowed(perms, full_key, value)
  return new_dict


def redact_op_outcome(op_outcome: ApiOperationOutcome) -> ApiOperationOutcome:
  perms = SharingPerms()
  return redact_for_perms(perms, 'operation_outcome.', op_outcome)
