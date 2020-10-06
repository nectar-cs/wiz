from typing import Dict, Optional

from k8kat.res.pod.kat_pod import KatPod

from nectwiz.model.base.resource_selector import ResourceSelector
from nectwiz.model.predicate.predicate import Predicate


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
