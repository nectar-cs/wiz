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


def interp(string: str, context: Dict) -> str:
  return string.format(SubsGetter(context or {}))
