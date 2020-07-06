from typing import Dict, Union, List

from wiz.model.base.validator import Validator

StrOrDict = Union[str, Dict[str, str]]

def parse_key_list(root: Union[List, str], all_keys: List) -> List:
  if type(root) == List:
    return root
  elif root == 'all':
    return all_keys
  else:
    print("DANGER bad state_recall target " + root)
    return []

def parse_recalled_state(root: Dict, all_keys) -> List:
  included = parse_key_list(root.get('included', []), all_keys)
  excluded = parse_key_list(root.get('excluded', []), all_keys)
  return list(set(included) - set(excluded))

def eval_next_expr(root: StrOrDict, values: Dict[str, str]) -> str:
  if type(root) == str:
    return root
  elif type(root) == dict:
    if is_ift_tree(root):
      logic_key = eval_cond_tree(root.get('if'), values)
      return root[logic_key]
    else:
      raise RuntimeError(f"Can't process {root}")
  else:
    raise RuntimeError(f"Can't evaluate {root}")


def is_ift_tree(root):
  return root.get('if') and root.get('then') and root.get('else')


def eval_cond_tree(conditions, values) -> str:
  outcome = True
  for condition in conditions:
    value = values[condition['field']]
    result = evaluate_condition(condition, value)
    if not result:
      outcome = False
  return "then" if outcome else "else"


def is_default_next(root: StrOrDict):
  if root is None:
    return True
  if type(root) == str and root == 'default':
    return True
  else:
    return False


def evaluate_condition(config, value):
  validator = Validator.inflate(config)
  return validator.perform(value)
