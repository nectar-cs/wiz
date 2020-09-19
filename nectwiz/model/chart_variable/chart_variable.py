from typing import Optional, List, TypeVar

from nectwiz.core.core import config_man, utils
from nectwiz.core.tam.tam_provider import tam_client
from nectwiz.core.core.utils import dict2keyed
from nectwiz.core.core.config_man import config_man
from nectwiz.model.base.wiz_model import WizModel

T = TypeVar('T', bound='ChartVariable')

class ChartVariable(WizModel):
  def __init__(self, config):
    super().__init__(config)
    self.data_type: str = config.get('type', 'string')
    self.explicit_default: str = config.get('default')
    self.mode: str = config.get('mode', 'internal')
    self.release_overridable: str = config.get('release_overridable', False)

  @property
  def default_value(self) -> str:
    """
    Getter for the default value of the chart variable.
    :return: the default value.
    """
    if self.explicit_default:
      return self.explicit_default
    return config_man.tam_defaults().get(self.id())

  @property
  def linked_res_name(self) -> str:
    """
    Getter for the linked resource name of the chart variable.
    :return: linked resource name.
    """
    return self.config.get('resource')

  def is_safe_to_set(self) -> bool:
    """
    Returns whether a variable is safe to set (considered such if its mode is
    set as "public").
    :return: True if safe to set, False otherwise.
    """
    return self.mode == 'public'

  def field(self):
    """
    Returns the field associated with the chart variable, if one exists, else
    returns None.
    :return: associated field or None.
    """
    from nectwiz.model.field.field import Field
    children = self.load_children('field', Field)
    return children[0] if len(children) == 1 else None

  def validate(self, value) -> List[Optional[str]]:
    """
    Retrieves the associated field and validates its value against a list of
    Validators.
    :param value: value to be validated.
    :return: list with [tone, message] or [None, None] if no associated field
    exists.
    """
    from nectwiz.model.field.field import Field
    field: Field = self.field()
    if field:
      return field.validate(value)
    else:
      return [None, None]

  def read_crt_value(self, force_reload=False) -> Optional[str]:
    """
    Reads the current value of the associated field. Tries to read from cache
    first, else dumps the ConfigMap and gets the value from there.
    :return: string containing the current value of the field.
    """
    root = config_man.mfst_vars(force_reload)
    return utils.deep_get(root, self.id().split('.'))

  def commit(self, value:str):
    """
    Use tami client to commit new values to an associated key. If the value is of
    mode "public", then also writes (applies) the manifest.
    :param value: value to be committed (and potentially applied).
    """
    config_man.commit_keyed_mfst_vars([(self.id(), value)])
    if self.is_safe_to_set():
      tam_client().apply(rules=None, inlines=None)

  def operations(self):
    """
    Inflates (instantiates) all the operations associated with the chart variable
    into instances of the Operation class.
    :return: list of inflated Operation objects.
    """
    from nectwiz.model.operation.operation import Operation
    return self.load_children('operations', Operation)

  @classmethod
  def all_vars(cls) -> List[T]:
    raw = config_man.mfst_vars(force_reload=True)
    committed_vars = dict2keyed(raw)
    models = cls.inflate_all()
    pres = lambda k: len([cv for cv in models if cv.id() == k]) > 0
    for committed_var in committed_vars:
      key = committed_var[0]
      if not pres(key):
        models.append(ChartVariable(dict(id=key)))
    return models

  @classmethod
  def release_dpdt_vars(cls) -> List[T]:
    matcher = lambda cv: cv.release_overridable == True
    return list(filter(matcher, ChartVariable.inflate_all()))
