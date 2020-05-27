from flask import Blueprint, jsonify, request

from wiz.model.chart_variable import serial
from wiz.model.chart_variable.chart_variable import ChartVariable

controller = Blueprint('variables_controller', __name__)


@controller.route('/api/chart-variables')
def chart_variables_index():
  chart_variables = ChartVariable.inflate_all()
  serialized = [serial.standard(cv) for cv in chart_variables]
  return jsonify(data=serialized)


@controller.route('/api/chart-variables/<key>')
def chart_variables_show(key):
  chart_variable = find_variable(key)
  return jsonify(data=serial.with_field(chart_variable))


@controller.route('/api/chart-variables/<key>/validate', methods=['POST'])
def chart_variables_validate(key):
  chart_variable = find_variable(key)
  value = request.json['value']
  tone, message = chart_variable.validate(value)
  if tone and message:
    return jsonify(data=dict(status=tone, message=message))
  else:
    return jsonify(data=dict(status='valid'))


def find_variable(key) -> ChartVariable:
  return ChartVariable.inflate(key)
