from flask import Blueprint, jsonify, request

from nectwiz.controllers.ctrl_utils import jparse
from nectwiz.core.core.config_man import config_man
from nectwiz.core.tam.tam_provider import tam_client
from nectwiz.model.variables import manifest_vars_serial
from nectwiz.model.variables.manifest_variable import ManifestVariable

BASE = '/api/manifest-variables'

controller = Blueprint('manifest_variables_controller', __name__)


@controller.route(BASE)
def manifest_variables_index():
  """
  Inflates and serializes the current list of chart variables.
  :return: serialized list of chart variables.
  """
  manifest_var_models = ManifestVariable.all_vars()
  serialize = lambda cv: manifest_vars_serial.standard(cv=cv)
  serialized = list(map(serialize, manifest_var_models))
  return jsonify(data=serialized)


@controller.route(f"{BASE}/defaults")
def manifest_variables_defaults():
  as_dict = config_man.read_manifest_defaults()
  return jsonify(data=as_dict)


@controller.route(f'{BASE}/commit-injections', methods=['POST'])
def manifest_variables_commit_injections():
  result = ManifestVariable.inject_server_defaults()
  return jsonify(data=result)


@controller.route(f'{BASE}/populate-defaults')
def chart_vars_populate_defaults():
  defaults = tam_client().load_manifest_defaults()
  config_man.write_mfst_defaults(defaults)
  return jsonify(data=defaults)


@controller.route(f'{BASE}/<key>')
def manifest_variable_show(key):
  """
  Finds and serializes the chart variable.
  :param key: key used to locate the right chart variable.
  :return: serialized chart variable.
  """
  variable_model = find_variable(key)
  serialized = manifest_vars_serial.full(variable_model)
  return jsonify(data=serialized)


@controller.route(f'{BASE}/<key>/submit', methods=['POST'])
def manifest_variable_submit(key):
  """
  Updates the chart variable with new value.
  :param key: key to locate the right chart variable.
  :return: status of the update.
  """
  value = request.json['value']
  variable_model = find_variable(key)
  variable_model.commit(value)
  return jsonify(status='success')


@controller.route(f'{BASE}/commit-apply', methods=['POST'])
def manifest_variables_commit_apply():
  """
  Updates the chart variable with new value.
  :return: status of the update.
  """
  assignments = list(request.json['assignments'].items())
  config_man.commit_keyed_mfst_vars(assignments)
  logs = tam_client().apply([])
  print(logs)
  return jsonify(status='success')


@controller.route(f'{BASE}/<key>/validate', methods=['POST'])
def manifest_variable_validate(key):
  """
  Validates the chart variable against
  :param key: key to locate the right chart variable.
  :return: validation status, with tone and message if unsuccessful.
  """
  variable_model = find_variable(key)
  value = jparse()['value']
  context = dict(resolvers=config_man.resolvers())
  eval_result = variable_model.validate(value, context)
  status = 'valid' if eval_result['met'] else eval_result['tone']
  message = None if eval_result['met'] else eval_result['reason']
  return jsonify(data=dict(status=status, message=message))


def find_variable(key) -> ManifestVariable:
  return ManifestVariable.inflate(key)
