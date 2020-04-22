from typing import Dict

from wiz.model.field.validator import Validator


def eval_next_expr(root, values: Dict[str, str]) -> str:
  if type(root) == str:
    return root
  elif type(root) == dict:
    if is_ift_tree(root):
      conditions: [Dict[str, str]] = root.get('if')
      logic_key = eval_cond_tree(conditions, values)
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
    value = values[condition.pop('field')]
    result = evaluate_condition(condition, value)
    if not result:
      outcome = False
  return "then" if outcome else "else"


def evaluate_condition(config, value):
  validator = Validator.inflate(config)
  return validator.perform(value)