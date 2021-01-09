from flask import Blueprint, jsonify

from nectwiz.core.core import job_client, updates_man
from nectwiz.core.telem import telem_man
# from nectwiz.core.core.updates_man import UpdateAction, WizUpdateAction

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


@controller.route(f'{BASE_PATH}/<update_id>/install', methods=['POST'])
def install_update(update_id):
  # bundle = updates_man.fetch_update(update_id)
  # job_id = job_client.enqueue_action(UpdateAction.__name__, update=bundle)
  # return jsonify(data=(dict(job_id=job_id)))
  pass


@controller.route(f'{BASE_PATH}/run-pre-wiz-update-hooks', methods=['POST'])
def run_pre_wiz_update_hooks():
  job_id = job_client.enqueue_action(mk_update_action('before'))
  return jsonify(data=(dict(job_id=job_id)))


@controller.route(f'{BASE_PATH}/run-post-wiz-update-hooks', methods=['POST'])
def run_post_wiz_update_hooks():
  job_id = job_client.enqueue_action(mk_update_action('after'))
  return jsonify(data=(dict(job_id=job_id)))


@controller.route(f'{BASE_PATH}/outcomes')
def list_past_updates():
  outcomes = telem_man.list_events()
  return jsonify(data=outcomes)


def mk_update_action(timing:  str):
  return dict(
    # kind=WizUpdateAction.__name__,
    when=timing
  )
