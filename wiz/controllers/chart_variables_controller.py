from flask import Blueprint, jsonify, request

from wiz.core import tedi_client
from wiz.model.chart_variable import serial
from wiz.model.chart_variable.chart_variable import ChartVariable

controller = Blueprint('variables_controller', __name__)


@controller.route('/api/chart-variables')
def chart_variables_index():
  """
  Fetches, inflates and serializes a list of chart variables.
  :return: serialized list of chart variables.
  """
  chart_dump = tedi_client.chart_dump()
  chart_variables = ChartVariable.inflate_all()
  serialize = lambda cv: serial.standard(cv=cv, cache=chart_dump)
  serialized = [serialize(cv) for cv in chart_variables]
  return jsonify(data=serialized)


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
  Updates the chart variable with new values.
  :param key: key to locate the right chart variable.
  :return: status of the update.
  """
  value = request.json['value']
  chart_variable = find_variable(key)
  chart_variable.commit(value)
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
