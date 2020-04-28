from wiz.core.types import K8sRes


class ResMatchRule:

  def __init__(self, expr: str):
    self.expr = expr
    parts = expr.split(':')
    self.kind_expr = parts[len(parts) - 2]
    self.name_expr = parts[len(parts) - 1]
    self.ns_expr = parts[0] if len(parts) == 3 else None

  def evaluate(self, res: K8sRes) -> bool:
    res_kind = res['kind']
    res_name = res['metadata']['name']
    res_ns = res['metadata'].get('namespace')

    tuples = [
      (self.ns_expr, res_ns),
      (self.kind_expr, res_kind),
      (self.name_expr, res_name)
    ]

    for rule, challenge in tuples:
      if not component_matches(rule, challenge):
        return False

    return True


def component_matches(rule_exp: str, challenge: str) -> bool:
  if rule_exp:
    if rule_exp == '*' or rule_exp == challenge:
      return True
    else:
      return False
  else:
    return True

