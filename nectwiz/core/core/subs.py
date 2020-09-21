from typing import Dict

class Getter:
  def __init__(self, src: Dict):
    self.src: Dict = src

  def __getitem__(self, k: str):
    direct_hit = self.src[k]
    resolver_desc = k.split("/")
    if direct_hit:
      if type(direct_hit) == str:
        return direct_hit
      elif callable(direct_hit):
        return direct_hit()
    elif len(resolver_desc) == 2:
      resolvers = self.src.get('resolvers', {})
      resolver = resolvers.get(resolver_desc[0])
      resolvable_key = resolver_desc[1]
      return resolver(resolvable_key) if resolver else None
  __getattr__ = __getitem__


def interp_str():
  pass


def deep_dict(root: Dict, sub_map: Dict) -> Dict:
  new_dict = {}

  def do_sub(var: any) -> any:
    return interp(var, sub_map) if type(var) == str else var

  for k, v in list(root.items()):
    if type(v) == dict:
      new_dict[k] = deep_dict(v, sub_map)
    elif type(v) == list:
      for i, item in v:
        if type(v) == dict:
          new_dict[k][i] = deep_dict(item, sub_map)
        else:
          new_dict[k][i] = do_sub(v)
    else:
      new_dict[k] = do_sub(v)
  return new_dict


def interp(string: str, context: Dict) -> str:
  return string.format(Getter(context or {}))
