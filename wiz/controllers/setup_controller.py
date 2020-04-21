import json
from flask import Blueprint, jsonify, request

from wiz.model.concern import serial as concern_serial
from wiz.model.step import serial as step_serial
from wiz.model.concern.concern import Concern
from wiz.model.step.step import Step

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


@controller.route(STEP_PATH)
def steps_show(concern_id, step_id):
  step = find_step(concern_id, step_id)
  serialized = step_serial.standard(step)
  return jsonify(serialized)


@controller.route(f'{STEP_PATH}/next')
def steps_next(step_id):
  pass


def find_concern(key) -> Concern:
  return Concern.inflate(key)


def find_step(concern_key, step_key) -> Step:
  concern = find_concern(concern_key)
  return concern.step(step_key)


def inflate_step_state():
  raw_state = request.headers.get('step_state')
  return json.loads(raw_state)
