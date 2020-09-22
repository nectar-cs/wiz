from flask import Blueprint, jsonify, request

from nectwiz.controllers.ctrl_utils import jparse
from nectwiz.core.core import hub_client
from nectwiz.core.core.config_man import config_man
from nectwiz.core.tam.tam_provider import tam_client
from nectwiz.model.variables import mfst_vars_serial
from nectwiz.model.variables.manifest_variable import ManifestVariable

BASE = '/api/manifest-variables'

controller = Blueprint('variables_controller', __name__)


@controller.route(BASE)
def chart_variables_index():
  """
  Inflates and serializes the current list of chart variables.
  :return: serialized list of chart variables.
  """
  manifest_var_models = ManifestVariable.all_vars()
  serialize = lambda cv: mfst_vars_serial.standard(cv=cv)
  serialized = list(map(serialize, manifest_var_models))
  return jsonify(data=serialized)


@controller.route(f'{BASE}/commit-injections', methods=['POST'])
def chart_vars_commit_injections():
  result = ManifestVariable.inject_server_defaults()
  return jsonify(data=result)


@controller.route('/api/chart-variables/populate-defaults')
def chart_vars_populate_defaults():
  defaults = tam_client().load_manifest_defaults()
  config_man.write_mfst_defaults(defaults)
  return jsonify(data=defaults)


@controller.route('/api/chart-variables/<key>')
def chart_variables_show(key):
  """
  Finds and serializes the chart variable.
  :param key: key used to locate the right chart variable.
  :return: serialized chart variable.
  """
  chart_variable = find_variable(key)
  return jsonify(data=serial.with_field(chart_variable))


@controller.route('/api/chart-variables/<key>/submit', methods=['POST'])
def chart_variables_submit(key):
  """
  Updates the chart variable with new value.
  :param key: key to locate the right chart variable.
  :return: status of the update.
  """
  value = request.json['value']
  chart_variable = find_variable(key)
  chart_variable.commit(value)
  return jsonify(status='success')


@controller.route('/api/chart-variables/commit-apply', methods=['POST'])
def chart_variables_commit_apply():
  """
  Updates the chart variable with new value.
  :return: status of the update.
  """
  assignments = list(request.json['assignments'].items())
  config_man.commit_keyed_mfst_vars(assignments)
  logs = tam_client().apply([])
  print(logs)
  return jsonify(status='success')


@controller.route('/api/manifest-variables/<key>/validate', methods=['POST'])
def chart_variables_validate(key):
  """
  Validates the chart variable against
  :param key: key to locate the right chart variable.
  :return: validation status, with tone and message if unsuccessful.
  """
  chart_variable = find_variable(key)
  value = jparse()['value']
  context = dict(resolvers=config_man.resolvers())
  eval_result = chart_variable.validate(value, context)
  status = 'valid' if eval_result['met'] else eval_result['tone']
  message = None if eval_result['met'] else eval_result['reason']
  return jsonify(data=dict(status=status, message=message))


def find_variable(key) -> ManifestVariable:
  return ManifestVariable.inflate(key)
