from typing import Dict

def deep_set(dict_root: Dict, names: [str], value: any):
  if len(names) == 1:
    dict_root[names[0]] = value
  else:
    if not dict_root.get(names[0]):
      dict_root[names[0]] = dict()
    deep_set(dict_root[names[0]], names[1:], value)
