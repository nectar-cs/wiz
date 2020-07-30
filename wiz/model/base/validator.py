from typing import Dict, Union, List
import validators


class Validator:
  """Field validator class."""

  def __init__(self, config: Dict[str, any]):
    self.config = config

  @property
  def check(self) -> Union[str,List]:
    """
    Getter for the "check against" property. Like the name suggests, defines
    the value the field is validated against.
    :return: value to be checked against.
    """
    return str(self.config.get('check_against', '')).lower()

  @property
  def message(self) -> str:
    """
    Getter for the message property. Messages are displayed to the user when they
    interact with an associated field.
    :return: message property.
    """
    return str(self.config.get('message'))

  @property
  def tone(self) -> str:
    """
    Getter for the tone property. Examples include "warning" and "error".
    Displayed as the result of the evaluation.
    :return: tone property.
    """
    return self.config.get('tone', 'error').lower()

  def perform(self, value) -> bool:
    """
    Parent method to perform the validation. Overwritten by specific types of
    validators.
    :param value: True if validation fails, False otherwise. NOTE:TRUE IF FAILS.
    """
    raise NotImplementedError

  def validate(self, value):
    """
    Performs validation using the appropriate Validator.
    :param value: value to be checked.
    :return: List containing [tone, message] if validation fails, else
    [None, None].
    """
    if self.perform(value):
      return [self.tone, self.message]
    else:
      return [None, None]

  @classmethod
  def inflate(cls, config) -> 'Validator':
    """
    Inflates (instantiates) the validator as an instance of the Validator class.
    :param config: config to be used for instantiation.
    :return: instance of Validator class.
    """
    _type = config['type']
    if _type == 'equality':
      return EqValidator(config)
    elif _type == 'inequality':
      return NeqValidator(config)
    elif _type == 'presence':
      return PresenceValidator(config)
    elif _type == 'format':
      return FormatValidator(config)
    else:
      raise RuntimeError(f"Don't know validation type {_type}")


class EqValidator(Validator):
  def perform(self, value):
    """
    Performs equality validation. Checks that the passed value matches
    the "checked against" property.
    :param value: value to be matched.
    :return: True if validation fails, False otherwise.
    """
    # todo TO BE REFACTORED
    return self.check == str(value).lower()


class NeqValidator(EqValidator):
  def perform(self, value):
    """
    Performs "not equals" validation. Checks that the passed value does not
    match the "checked against" property.
    :param value: value to be checked.
    :return: True if validation fails, False otherwise.
    """
    return not super().perform(value)


class PresenceValidator(Validator):
  @property
  def message(self):
    return self.config.get('message', 'Cannot be empty')

  @property
  def check(self) -> bool:
    """
    Overwrites the parent's "check against" property into a boolean.
    :return: True if check_against is set to True or empty, else False.
    """
    given = str(self.config.get('check_against', 'True')).lower()
    return given == 'true'

  def perform(self, value):
    """
    Performs presence validation.
    :param value: value to be checked for presence.
    :return: True if validation fails, False otherwise.
    """
    if self.check:
      return not bool(value)
    else:
      # if value is empty, we return False, which means there is no error message
      return bool(value)


class FormatValidator(Validator):
  @property
  def message(self):
    default = f'Must be {self.inflection()} {self.check}'
    return self.config.get('message', default)

  def inflection(self) -> str:
    """
    Returns the appropriate inflection for the "check against" property.
    :return: "a" or "an".
    """
    return 'an' if self.check in ['integer', 'email'] else 'a'

  def perform(self, value):
    """
    Performs type validation.
    :param value: value to be checked.
    :return: True if validation fails, False otherwise.
    """
    if self.check == 'integer':
      return not value.isdigit()
    elif self.check == 'boolean':
      return value not in ['true', 'false']
    elif self.check == 'email':
      return not validators.email(value)
    elif self.check == 'domain':
      return not validators.domain(value)
    else:
      raise RuntimeError(f"NO ADAPTER FOR {self.check}")
