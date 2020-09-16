from typing import Dict, List, Optional

from nectwiz.core.core.config_man import config_man
from nectwiz.core.core.utils import deep_get
from nectwiz.model.base.res_match_rule import ResMatchRule
from nectwiz.model.base.wiz_model import WizModel


TYPE_TEXT = 'text'
TYPE_SELECT = 'select'


class Input(WizModel):

  def __init__(self, config: Dict):
    super().__init__(config)
    self._type = config.get('type', TYPE_TEXT)
    self.option_descriptors = config.get('options')
    self.options_source = config.get('options_source', None)
    self.expl_default = config.get('default')
    self.validation_descriptors = config.get('validations', [
      dict(type='presence')
    ])

  def type(self):
    return self._type

  def default_value(self) -> Optional[str]:
    if self.expl_default:
      return self.expl_default
    else:
      variable_id = self.parent and self.parent.id()
      if variable_id:
        tam_defaults = config_man.tam_defaults() or {}
        return deep_get(tam_defaults, self.id().split("."))
      else:
        if self._type == TYPE_SELECT:
          options = self.options()
          return options[0].get('id') if len(options) > 0 else None
        else:
          return None

  def options(self) -> List[dict]:
    if self.options_source:
      _type = self.options_source.get('type')
      if _type == 'select-k8s-res':
        rule_descriptors = self.options_source.get('res_match_rules', [])
        rules = [ResMatchRule(rd) for rd in rule_descriptors]
        res_list = set(sum([rule.query() for rule in rules], []))
        return [{'id': r.name, 'value': r.name} for r in res_list]
      else:
        raise RuntimeError(f"Can't process source {type}")
    else:
      return self.option_descriptors
