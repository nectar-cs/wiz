from flask import Blueprint, jsonify

from nectwiz.core.job import job_client
from nectwiz.core.telem import updates_man

controller = Blueprint('app_controller', __name__)

BASE_PATH = '/api/updates'


@controller.route(f'{BASE_PATH}/next-available')
def fetch_next_available():
  bundle = updates_man.next_available()
  return jsonify(data=bundle)


@controller.route(f'{BASE_PATH}/install-next-available', methods=['POST'])
def app_apply_update():
  updater = updates_man.install_next_available
  job_id = job_client.enqueue_func(updater)
  return jsonify(data=(dict(job_id=job_id)))
