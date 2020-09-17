from typing import Dict, Union, List

from nectwiz.core.core import subs
from nectwiz.model.predicate.predicate import Predicate


def eval_next_expr(root: any, sub_map: Dict[str, str]) -> str:
  if not root or type(root) == str:
    return none_if_default(root)
  elif type(root) == dict and is_ift_tree(root):
    desc = root.get('if')
    desc = subs.deep_sub(desc, sub_map) if type(desc) == dict else desc
    predicate = Predicate.inflate(desc)
    outcome = predicate.evaluate()
    logic_key = 'then' if outcome else 'else'
    return none_if_default(root.get(logic_key))
  else:
    raise RuntimeError(f"Can't evaluate {root}")


def is_ift_tree(root: Union[str, Dict[str, str]]) -> bool:
  """
  Checks if the passed root is an instance of if/then/else tree.
  :param root: root to be checked, string or dict.
  :return: True if all 3 of if, then, else present as keys in root.
  """
  glob = root.get('if') and root.get('then') and root.get('else')
  return glob is not None


def none_if_default(root):
  """
  Checks if passed step evaluates to "default" or is None.
  :param root: passed step in string or dict form.
  :return: True if it does, False otherwise.
  """
  if root is None:
    return None
  if type(root) == str and root == 'default':
    return None
  else:
    return root
