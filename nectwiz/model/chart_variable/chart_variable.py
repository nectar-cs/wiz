from typing import Optional, List

from nectwiz.core import config_man, utils
from nectwiz.core.tam import tami_client
from nectwiz.core.tam.tam_provider import tam_client
from nectwiz.model.base.wiz_model import WizModel


class ChartVariable(WizModel):

  @property
  def data_type(self) -> str:
    """
    Getter for chart variable's data type. Defaults to string.
    :return: chart variable's data type.
    """
    return self.config.get('type', 'string')

  @property
  def is_ephemeral(self) -> bool:
    """
    Getter for the ephemeral option of chart variable. Defaults to false.
    :return: True if ephemeral, False otherwise.
    """
    return self.config.get('ephemeral', False)

  @property
  def default_value(self) -> str:
    """
    Getter for the default value of the chart variable.
    :return: the default value.
    """
    return self.config.get('default')

  @property
  def linked_res_name(self) -> str:
    """
    Getter for the linked resource name of the chart variable.
    :return: linked resource name.
    """
    return self.config.get('resource')

  @property
  def mode(self) -> str:
    """
    Getter for the mode of the chart variable. Options include
      - public - least constraining type, variable is easily visible / editable
      - internal - variable is an internal setting and should be adjusted with care
      - secret - variable is encrypted and should not be interpreted directly
      - coupled - variable should be set together with another variable
    :return: variable's mode
    """
    return self.config.get('mode', 'internal')

  @property
  def category(self) -> str:
    """
    Getter for the category of a chart variable. Examples include "storage",
    "application", "networking", "performance".
    :return: variable's category.
    """
    return self.config.get('category')

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

  def read_crt_value(self, cache=None) -> Optional[str]:
    """
    Reads the current value of the associated field. Tries to read from cache
    first, else dumps the ConfigMap and gets the value from there.
    :param cache: cache object to be checked first.
    :return: string containing the current value of the field.
    """
    if cache is not None:
      return utils.deep_get(cache, self.key.split('.'))
    else:
      return config_man.read_tam_var(self.key)

  def commit(self, value:str):
    """
    Use tami client to commit new values to an associated key. If the value is of
    mode "public", then also writes (applies) the manifest.
    :param value: value to be committed (and potentially applied).
    """
    config_man.commit_keyed_tam_assigns([(self.key, value)])
    if self.is_safe_to_set():
      tam_client().apply(rules=None, inlines=None)

  def operations(self):
    """
    Inflates (instantiates) all the operations associated with the chart variable
    into instances of the Operation class.
    :return: list of inflated Operation objects.
    """
    from nectwiz.model.operations.operation import Operation
    return self.load_children('operations', Operation)