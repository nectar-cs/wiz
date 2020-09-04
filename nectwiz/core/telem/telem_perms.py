from typing import Dict, Optional

from k8kat.res.config_map.kat_map import KatMap
from werkzeug.utils import cached_property

from nectwiz.core import config_man

cmap_field = 'sharing_prefs'
upload_telem_key = 'upload_telem'


class TelemPerms:
  """This class is responsible for Telemetry screen in the Pre-installation."""

  @cached_property
  def master_cmap(self) -> KatMap:
    """
    Uses Tami client to return the ConfigMap.
    :return: ConfigMap object.
    """
    return config_man.master_cmap()

  def user_perms(self) -> Dict:
    """
    Gets the default "sharing prefs" value from the ConfigMap.
    :return: dict with sharing prefs.
    """
    kat_map = self.master_cmap
    return kat_map.jget(cmap_field, {}) if kat_map else {}

  def patch(self, values: Dict):
    """
    Inserts the passed values into the user_perms dictionary.
    :param values: key-value pairs to be isnerted.
    """
    values = {k: v for k, v in values.items() if v is not None}
    if self.master_cmap:
      merged = {**self.user_perms(), **values}
      self.master_cmap.jpatch(merged, cmap_field, merge=False)

  def can_sync_telem(self) -> bool:
    """
    Gets the "upload telem" key from user_perms and converts it to a boolean.
    This defines the permission to sync telem information with the database.
    :return:
    """
    return x_to_bool(self.user_perms().get(upload_telem_key))

  def can_share_prop(self, prop: str) -> bool:
    """
    Gets the value of the category that matches the passed property from
    user_perms and converts it to boolean.
    :param prop: property to find the category.
    :return: True if value is True, otherwise False.
    """
    category = find_prop_category(prop)
    return x_to_bool(category and self.user_perms().get(category))


def x_to_bool(raw) -> bool:
  """
  Converts string / None / bool to bool.
  :param raw: input to be converted.
  :return: boolean value.
  """
  if raw is None:
    return False
  elif type(raw) == bool:
    return raw
  elif type(raw) == str:
    return raw.lower() == 'true'


def find_prop_category(prop) -> Optional[str]:
  """
  Returns category based on category property.
  :param prop: category property.
  :return: category.
  """
  for category, category_props in category_props_mapping.items():
    if prop in category_props:
      return category
  return None


category_props_mapping = {
  'telem.persist': [],
  'telem.upload': [],
  'telem.share_vendor': [],
  'operations.metadata': [
    'operation_outcome.operation_id',
    'operation_outcome.step_outcomes',
    'operation_outcome.step_outcomes.stage_id',
    'operation_outcome.step_outcomes.step_id',
    'operation_outcome.step_outcomes.started_at',
    'operation_outcome.step_outcomes.terminated_at',
    'operation_outcome.step_outcomes.job_logs',
    'operation_outcome.step_outcomes.commit_outcome',
    'operation_outcome.step_outcomes.exit_condition_outcomes',
    'operation_outcome.step_outcomes.exit_condition_outcomes.condition_id',
    'operation_outcome.step_outcomes.exit_condition_outcomes.condition_met',
    'operation_outcome.step_outcomes.exit_condition_outcomes.reason'
  ],
  'operations.assignments': [
    'operation_outcome.step_outcomes.chart_assigns',
    'operation_outcome.step_outcomes.state_assigns',
  ],
  'operations.asd': [

  ]
}
