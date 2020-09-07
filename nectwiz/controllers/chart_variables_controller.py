from flask import Blueprint, jsonify, request

from nectwiz.core.core import hub_client, config_man
from nectwiz.core.tam.tam_provider import tam_client
from nectwiz.core.core.wiz_app import wiz_app
from nectwiz.model.chart_variable import serial
from nectwiz.model.chart_variable.chart_variable import ChartVariable

controller = Blueprint('variables_controller', __name__)


@controller.route('/api/chart-variables')
def chart_variables_index():
  """
  Inflates and serializes the current list of chart variables.
  :return: serialized list of chart variables.
  """
  chart_variables = ChartVariable.all_vars()
  serialize = lambda cv: serial.standard(cv=cv)
  serialized = [serialize(cv) for cv in chart_variables]
  return jsonify(data=serialized)


@controller.route('/api/chart-variables/commit-injections', methods=['POST'])
def chart_vars_commit_injections():
  install_uuid = wiz_app.install_uuid(force_reload=True)
  if install_uuid:
    route = f'/installs/{install_uuid}/injections'
    resp = hub_client.get(route)
    injections = None
    if resp.status_code < 300:
      injections = resp.json().get('data')
      if injections:
        config_man.commit_tam_assigns(injections)
    return jsonify(data=injections)
  else:
    print("Install UUID not found!")
    return {}


@controller.route('/api/chart-variables/populate-defaults')
def chart_vars_populate_defaults():
  defaults = tam_client().load_manifest_defaults()
  config_man.write_tam_var_defaults(defaults)
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
  config_man.commit_keyed_tam_assigns(assignments)
  logs = tam_client().apply([])
  print(logs)
  return jsonify(status='success')


@controller.route('/api/chart-variables/<key>/validate', methods=['POST'])
def chart_variables_validate(key):
  """
  Validates the chart variable against
  :param key: key to locate the right chart variable.
  :return: validation status, with tone and message if unsuccessful.
  """
  chart_variable = find_variable(key)
  value = request.json['value']
  tone, message = chart_variable.validate(value)
  if tone and message:
    return jsonify(data=dict(status=tone, message=message))
  else:
    return jsonify(data=dict(status='valid'))


def find_variable(key) -> ChartVariable:
  return ChartVariable.inflate(key)
