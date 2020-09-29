from flask import Blueprint, jsonify

from nectwiz.core.core import job_client
from nectwiz.core.telem import updates_man, telem_man

controller = Blueprint('updates_controller', __name__)

BASE_PATH = '/api/updates'


@controller.route(f'{BASE_PATH}/next-available')
def fetch_next_available():
  bundle = updates_man.next_available()
  return jsonify(data=bundle)


@controller.route(f'{BASE_PATH}/<update_id>')
def show_update(update_id):
  bundle = updates_man.fetch_update(update_id)
  return jsonify(data=bundle)


@controller.route(f'{BASE_PATH}/<update_id>/install', methods=['POST'])
def install_update(update_id):
  bundle = updates_man.fetch_update(update_id)
  updater = updates_man.install_update
  job_id = job_client.enqueue_func(updater, bundle)
  return jsonify(data=(dict(job_id=job_id)))


@controller.route(f'{BASE_PATH}/install-next-available', methods=['POST'])
def install_next_available():
  updater = updates_man.install_next_available
  job_id = job_client.enqueue_func(updater)
  return jsonify(data=(dict(job_id=job_id)))


@controller.route(f'{BASE_PATH}/outcomes')
def list_past_updates():
  outcomes = telem_man.list_update_outcomes()
  return jsonify(data=outcomes)
