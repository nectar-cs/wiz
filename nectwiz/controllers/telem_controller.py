from flask import Blueprint, jsonify

from nectwiz.core.telem import telem_man

controller = Blueprint('telem_controller', __name__)

BASE = '/api/telem'


@controller.route(f'{BASE}/prefs')
def prefs_show():
  return jsonify(ping='pong')


@controller.route(f'{BASE}/prefs', methods=['PATCH'])
def prefs_patch():
  return jsonify(ping='pong')


@controller.route(f'{BASE}/outcomes')
def list_outcomes():
  return jsonify(data=telem_man.list_outcomes())


@controller.route(f'{BASE}/config_backups')
def list_config_backups():
  return jsonify(data=telem_man.list_config_backups())
