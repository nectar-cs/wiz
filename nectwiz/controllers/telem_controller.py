from datetime import datetime

from flask import Blueprint, jsonify

from nectwiz.controllers.ctrl_utils import jparse
from nectwiz.core.core.config_man import config_man
from nectwiz.core.telem import telem_man
from nectwiz.serializers import telem_serializers

controller = Blueprint('telem_controller', __name__)

BASE = '/api/telem'


@controller.route(f'{BASE}/prefs')
def prefs_show():
  return jsonify(ping='pong')


@controller.route(f'{BASE}/prefs', methods=['PATCH'])
def prefs_patch():
  return jsonify(ping='pong')


@controller.route(f'{BASE}/config_backups/new', methods=['POST'])
def new_config_backup():
  attrs = jparse()
  config_backup = dict(
    name=attrs.get('name') or 'none',
    event_type='client_triggered',
    data=config_man.serialize(),
    timestamp=str(datetime.now())
  )
  result = telem_man.store_config_backup(config_backup)
  return jsonify(id=str(result.inserted_id), record=config_backup)


@controller.route(f'{BASE}/events')
def list_events():
  return jsonify(data=telem_man.list_events())


@controller.route(f'{BASE}/config_backups/<config_id>')
def config_backups_show(config_id: str):
  record = telem_man.get_config_backup(config_id)
  print(record)
  if record:
    serialized = telem_serializers.ser_config_backup_full(record)
    return jsonify(data=serialized)
  else:
    return jsonify(error='dne'), 404


@controller.route(f'{BASE}/config_backups')
def config_backups_index():
  records = telem_man.list_config_backups()
  serializer = telem_serializers.ser_config_backup
  return jsonify(data=list(map(serializer, records)))
