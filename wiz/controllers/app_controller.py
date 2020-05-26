from typing import List, Callable

from flask import Blueprint, jsonify
from k8_kat.res.dep.kat_dep import KatDep

from wiz.core.wiz_globals import wiz_app
from wiz.model.operations import serial
from wiz.model.operations.install_stage import InstallStage
from wiz.model.operations.operation import Operation

controller = Blueprint('app_controller', __name__)

BASE_PATH = '/api/app'

@controller.route(f'{BASE_PATH}/access_points', methods=["GET"])
def access_points():
  delegate: Callable = wiz_app.access_point_delegate
  if delegate:
    access_point_list = delegate()
    return jsonify(data=access_point_list)
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


@controller.route(f'{BASE_PATH}/install_stages')
def install_stages():
  stages_list = InstallStage.inflate_all()
  dicts = [serial.standard(c) for c in stages_list]
  return jsonify(data=dicts)


@controller.route(f'{BASE_PATH}/operations')
def operations():
  operations_list = Operation.inflate_all()
  dicts = [serial.standard(c) for c in operations_list]
  return jsonify(data=dicts)
