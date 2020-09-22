from flask import Blueprint, jsonify

controller = Blueprint('telem_controller', __name__)

BASE = '/api/telem'

@controller.route(f'{BASE}/prefs')
def prefs_show():
  return jsonify(ping='pong')


@controller.route(f'{BASE}/prefs', methods=['PATCH'])
def prefs_patch():
  return jsonify(ping='pong')


