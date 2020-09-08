from typing import Dict, Union, List

from nectwiz.model.base.validator import Validator


StrOrDict = Union[str, Dict[str, str]]


def parse_key_list(root: Union[List, str], all_keys: List) -> List:
  """
  Returns either keys in root or all_keys.
  :param root: can be a list (in which case returns) or "all" (in which case
  all_keys is returned).
  :param all_keys: list of all possible keys as a backup.
  :return: a list of keys.
  """
  if type(root) == list:
    return root
  elif root == 'all':
    return all_keys
  else:
    print(f"DANGER bad state_recall target {root}")
    return []

def eval_next_expr(root: StrOrDict, values: Dict[str, str]) -> str:
  """
  Evaluates the next step. If the step is provided as a string, it's an explicit
  next step. If the step is provided as a dict, it's a if-then-else type step.
  :param root: next step in string or dict form.
  :param values: if-then-else values, if necessary.
  :return: string containing next step.
  """
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


def is_ift_tree(root: StrOrDict):
  """
  Checks if the passed root is an instance of if/then/else tree.
  :param root: root to be checked, string or dict.
  :return: True if all 3 of if, then, else present as keys in root.
  """
  return root.get('if') and root.get('then') and root.get('else')


def eval_cond_tree(conditions, values) -> str:
  """
  Evaluates the values against respective conditions.
  :param conditions: conditions to be evaluated.
  :param values: values to be checked.
  :return: returns "then" clause if all conditions for all values evaluate
  successfully, "else" clause otherwise.
  """
  outcome = True
  for condition in conditions:
    value = values[condition['field']]
    result = evaluate_condition(condition, value) #True = fail
    if not result:
      outcome = False #True leads to False
  return "then" if outcome else "else" #False leads to "else"


def is_default_next(root: StrOrDict) -> bool:
  """
  Checks if passed step evaluates to "default" or is None.
  :param root: passed step in string or dict form.
  :return: True if it does, False otherwise.
  """
  if root is None:
    return True
  if type(root) == str and root == 'default':
    return True
  else:
    return False


def evaluate_condition(config, value):
  """
  Instantiates the Validator and performs the validation.
  :param config: config to be used for Validator instantiation.
  :param value: value to be checked.
  :return: returns True if validation fails, False otherwise. NOTE: TRUE IF FAILS.
  """
  validator = Validator.inflate(config)
  return validator.perform(value)
