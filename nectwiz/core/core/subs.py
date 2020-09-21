from typing import Dict

class SubsGetter:
  def __init__(self, src: Dict):
    self.src: Dict = src

  def __getitem__(self, k: str):
    direct_hit = self.src.get(k)
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
    else:
      return None
  __getattr__ = __getitem__


def interp_dict_vals(root: Dict, context: Dict) -> Dict:
  new_dict = {}

  def do_sub(var: any) -> any:
    return interp(var, context) if type(var) == str else var

  for k, v in list(root.items()):
    if type(v) == dict:
      new_dict[k] = interp_dict_vals(v, context)
    elif type(v) == list:
      for i, item in v:
        if type(v) == dict:
          new_dict[k][i] = interp_dict_vals(item, context)
        else:
          new_dict[k][i] = do_sub(v)
    else:
      new_dict[k] = do_sub(v)
  return new_dict


def interp(string: str, context: Dict) -> str:
  fmt_string = string.replace("{", "{0.")
  return fmt_string.format(SubsGetter(context or {}))
