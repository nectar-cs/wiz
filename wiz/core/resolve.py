import importlib

import inflection

from wiz.core.wiz_globals import wiz_globals


def base_package():
  return wiz_globals.package_base


def find_item_class(kind, key):
  pass


def key_to_class_name(_key, kind):
  return inflection.camelize(f"{_key}_{kind}", True)


def key_to_module_name(_key, base, kind):
  return inflection.camelize(f"{base}.{_key}_{kind}", True)


def find_class(_key, pkg_name, kind):
  module_name = key_to_module_name(_key, pkg_name, kind)
  class_name = key_to_class_name(_key, kind)
  module = importlib.import_module(module_name)
  return getattr(module, class_name)


def find_concern_class(_key, backup):
  concerns_pkg_name = wiz_globals.concerns_package
  return find_class(_key, concerns_pkg_name, 'concern')

def find_step_class(_key, backup):
  steps_pkg_name = wiz_globals.steps_base
  return find_class(_key, steps_pkg_name, 'step')
