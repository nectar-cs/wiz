from typing import Dict


def deep_sub(root: Dict, sub_map: Dict) -> Dict:
  new_dict = {}

  def do_sub(var: any) -> any:
    return poly_interp(var, sub_map) if type(var) == str else var

  for k, v in list(root.items()):
    if type(v) == dict:
      new_dict[k] = deep_sub(v,  sub_map)
    elif type(v) == list:
      for i, item in v:
        if type(v) == dict:
          new_dict[k][i] = deep_sub(item,  sub_map)
        else:
          new_dict[k][i] = do_sub(v)
    else:
      new_dict[k] = do_sub(v)
  return new_dict


def poly_interp(source: str, sub_map: Dict) -> str:
  for substring, replacement in sub_map.items():

    substitute = replacement
    if callable(replacement):
      substitute = replacement()
    source = source.replace(substring, replacement)
  return source
