from typing import Dict

def deep_set(dict_root: Dict, names: [str], value: any):
  if len(names) == 1:
    print(f"Final assign {names[0]} := {value}")
    dict_root[names[0]] = value
  else:
    print(f"Now names is {names}")
    if not dict_root.get(names[0]):
      print(f"{dict_root} was empty")
      dict_root[names[0]] = dict()
    deep_set(dict_root[names[0]], names[1:], value)
