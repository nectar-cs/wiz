from flask import Blueprint, request, jsonify

from wiz.core import tedi_prep, tedi_client, res_watch
from wiz.core import wiz_globals

controller = Blueprint('status_controller', __name__)


@controller.route('/api/status')
def status():
  pod = tedi_client.tedi_pod()
  if pod:
    if pod.has_settled():
      if pod.is_running_normally():
        _status = 'ready'
      else:
        _status = 'error'
    else:
      _status = 'initializing'
  else:
    _status = 'none'

  return jsonify(status=_status)


@controller.route('/api/status/init', methods=['POST'])
def init():
  if not tedi_client.tedi_pod():
    params = request.json
    print("IM HERE")
    print(params)
    app, ns = params['app'], params['ns']
    print(app)
    print(ns)
    wiz_globals.persist_ns_and_app(ns, app)
    tedi_prep.create(ns, app)
  return dict(status='preparing')

