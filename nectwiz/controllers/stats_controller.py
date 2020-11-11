from flask import Blueprint, jsonify

from nectwiz.model.stats.basic_resource_metrics_computer import BasicResourceMetricsComputer

controller = Blueprint('stats_controller', __name__)

BASE_PATH = '/api/stats'

@controller.route(f'{BASE_PATH}/basic-resource-consumption')
def list_events():
  computer = BasicResourceMetricsComputer.inflate_singleton()
  return jsonify(data=computer.compute())
