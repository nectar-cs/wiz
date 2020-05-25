from flask import Blueprint, request, jsonify
from k8_kat.auth.kube_broker import broker

from wiz.core import tedi_prep, tedi_client
from wiz.core import wiz_globals

controller = Blueprint('status_controller', __name__)



@controller.route('/api/status')
def status():
  return jsonify(
    is_k8_kat_connected=broker.is_connected,
    last_k8_kat_conn_error=broker.last_error,
    connect_config=broker.connect_config
  )


@controller.route('/api/tedi/status')
def tedi_status():
  pod = tedi_client.tedi_pod()
  _status = pod.ternary_status() if pod else 'none'
  return jsonify(status=_status)


@controller.route('/api/tedi/prepare', methods=['POST'])
def tedi_init():
  if not tedi_client.tedi_pod():
    params = request.json
    app, ns = params['app'], params['ns']
    wiz_globals.persist_ns_and_app(ns, app)
    tedi_prep.create(ns, app)
  return dict(status='pending')
