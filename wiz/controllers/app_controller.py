from typing import List

from flask import Blueprint, jsonify, request
from k8_kat.res.dep.kat_dep import KatDep

from wiz.core import wiz_globals
from wiz.core.wiz_globals import wiz_app
from wiz.model.adapters.app_endpoint_adapter import AppEndpointAdapter

controller = Blueprint('app_controller', __name__)

BASE_PATH = '/api/app'


@controller.route(f'{BASE_PATH}/prepare', methods=['POST'])
def tedi_init():
  params = request.json
  app, ns = params['app'], params['ns']
  wiz_globals.persist_ns_and_app(ns, app)
  return dict(status='success')


@controller.route(f'{BASE_PATH}/application_endpoints', methods=["GET"])
def application_endpoints():
  provider = wiz_app.find_provider(AppEndpointAdapter)()
  if provider:
    adapters = provider.produce_adapters()
    ser_endpoints = [a.serialize() for a in adapters]
    return jsonify(data=ser_endpoints)
  else:
    return jsonify(data=[])


@controller.route(f'{BASE_PATH}/workload_versions', methods=["GET"])
def workload_versions():
  ns = wiz_app.ns
  kat_deps: List[KatDep] = KatDep.list(ns=ns)
  version_list = []
  for res in kat_deps:
    if res.name != 'nectar-wizard':
      version = res.annotations.get('nectar-version') or \
                res.annotations.get('version')
      last_update_at = res.annotations.get('last-updated-at')
      version_list.append(dict(
        workload=res.name,
        version=version,
        last_update_at=last_update_at
      ))
  return jsonify(data=version_list)
