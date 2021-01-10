from flask import Blueprint, jsonify

from nectwiz.core.core import job_client, updates_man
from nectwiz.core.telem import telem_man
from nectwiz.model.action.actions.apply_update_action import ApplyUpdateAction
from nectwiz.model.action.actions.run_update_hooks_action import RunUpdateHooksAction

controller = Blueprint('updates_controller', __name__)

BASE_PATH = '/api/updates'


@controller.route(f'{BASE_PATH}/next-available')
def fetch_next_available():
  telem_man.upload_status()
  bundle = updates_man.next_available()
  return jsonify(data=bundle)


@controller.route(f'{BASE_PATH}/<update_id>')
def show_update(update_id):
  bundle = updates_man.fetch_update(update_id)
  return jsonify(data=bundle)


@controller.route(f'{BASE_PATH}/<update_id>/preview')
def preview_update(update_id):
  update = updates_man.fetch_update(update_id)
  bundle = updates_man.preview(update)
  return jsonify(bundle)


@controller.route(f'{BASE_PATH}/<update_id>/apply', methods=['POST'])
def install_update(update_id):
  job_id = job_client.enqueue_action(dict(
    kind=ApplyUpdateAction.kind(),
    update_id=update_id,
  ))
  return jsonify(data=(dict(job_id=job_id)))


@controller.route(f'{BASE_PATH}/<update_id>/run_hooks/<_when>', methods=['POST'])
def run_pre_wiz_update_hooks(update_id: str, _when: str):
  job_id = job_client.enqueue_action(dict(
    kind=RunUpdateHooksAction.kind(),
    update_id=update_id,
    when=_when
  ))
  return jsonify(data=(dict(job_id=job_id)))


@controller.route(f'{BASE_PATH}/outcomes')
def list_past_updates():
  outcomes = telem_man.list_events()
  return jsonify(data=outcomes)
