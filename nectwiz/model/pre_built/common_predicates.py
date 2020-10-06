from typing import Dict, Optional

import validators
from k8kat.res.pod.kat_pod import KatPod

from nectwiz.core.core.config_man import config_man
from nectwiz.model.base.resource_selector import ResourceSelector
from nectwiz.model.predicate.predicate import Predicate


class ManifestVariablePredicate(Predicate):
  def __init__(self, config):
    super().__init__(config)
    self.variable_name = config.get('variable')

  def evaluate(self, context: Dict) -> bool:
    current_value = config_man.manifest_var(self.variable_name)
    return self._common_compare(current_value)


class ResourceCountPredicate(Predicate):
  def __init__(self, config):
    super().__init__(config)
    self.selector_config = config.get('selector')

  def evaluate(self, context: Dict) -> bool:
    res_list = self.selector().query_cluster(context)
    return self._common_compare(len(res_list))

  def selector(self) -> ResourceSelector:
    return ResourceSelector.inflate(self.selector_config)


class FormatPredicate(Predicate):

  def __init__(self, config: Dict):
    super().__init__(config)
    self.reason = f"Must be a(n) {self.check_against}"

  def evaluate(self, context: Dict) -> bool:
    check = self.check_against
    challenge = str(context.get('value', self.challenge))
    if check in ['integer', 'int', 'number']:
      return challenge.isdigit()
    elif check in ['boolean', 'bool']:
      return challenge not in ['true', 'false']
    elif check == 'email':
      return validators.email(challenge)
    elif check == 'domain':
      return validators.domain(challenge)


class MultiPredicate(Predicate):
  def __init__(self, config: Dict):
    super().__init__(config)
    self.operator = config.get('operator', 'and')

  def evaluate(self, context: Dict) -> bool:
    sub_preds = self.load_children('sub_predicates', Predicate)
    for sub_pred in sub_preds:
      evaluated_to_true = sub_pred.evaluate(context)
      if self.operator == 'or':
        if evaluated_to_true:
          return True
      elif self.operator == 'and':
        if not evaluated_to_true:
          return False
      else:
        print(f"[nectwiz::multipredicate] illegal operator {self.operator}")
        return False
    if self.operator == 'or':
      return False
    elif self.operator == 'and':
      return True
    else:
      print(f"[nectwiz::multipredicate] illegal operator {self.operator}")
      return False


class PodShellPredicate(Predicate):
  def __init__(self, config: Dict):
    super().__init__(config)
    self.selector_config = config.get('selector')
    self.command = config.get('command', 'echo hello')

  def selector(self) -> ResourceSelector:
    expr = self.selector_config
    return ResourceSelector.inflate(expr)

  def evaluate(self, context: Dict) -> bool:
    res_list = self.selector().query_cluster(context)
    res: Optional[KatPod] = res_list[0] if len(res_list) > 0 else None
    if res and type(res) == KatPod:
      output = res.shell_exec(self.command)
      return self._common_compare(output)


class PodHttpPredicate(Predicate):
  def __init__(self, config: Dict):
    super().__init__(config)
    self.selector_config = config.get('selector')
    self.command = config.get('endpoint', '/')
    self.check_type = config.get('check_type')

  def evaluate(self, context: Dict) -> bool:
    pass

  def selector(self) -> ResourceSelector:
    expr = self.selector_config
    return ResourceSelector.inflate(expr)
