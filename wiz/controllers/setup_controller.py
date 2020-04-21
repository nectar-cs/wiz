import json
from flask import Blueprint, jsonify, request

from wiz.model.concern import serial as concern_serial
from wiz.model.step import serial as step_serial
from wiz.model.concern.concern import Concern

CONCERNS_PATH = '/api/concerns'
CONCERN_PATH = f'/{CONCERNS_PATH}/<concern_id>'
STEPS_PATH = f'{CONCERN_PATH}/steps'
STEP_PATH = f'{STEPS_PATH}/<step_id>'
FIELD_PATH = f'{STEP_PATH}/fields/<field_id>'

controller = Blueprint('setup_controller', __name__)


@controller.route(CONCERNS_PATH)
def concerns_index():
  concerns = Concern.all()
  dicts = [concern_serial.standard(c) for c in concerns]
  return jsonify(data=dicts)

def concerns_show():
  pass

@controller.route(f'{STEP_PATH}/first_step')
def first_step_show(concern_id):
  concern = find_concern(concern_id)
  step = concern.first_step()
  serialized = step_serial.standard(step)
  return jsonify(serialized)

@controller.route(STEP_PATH)
def steps_show(concern_id, step_id):
  pass




@controller.route(f'{STEPS_PATH}/<step_id>')
def next_step(step_id):
  pass


def find_concern(key):
  return Concern.inflate(key)

def inflate_step_state():
  raw_state = request.headers.get('step_state')
  return json.loads(raw_state)
