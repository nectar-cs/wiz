from typing import List, Callable

from flask import Blueprint, jsonify
from k8_kat.res.dep.kat_dep import KatDep

from wiz.core.wiz_globals import wiz_globals

controller = Blueprint('app_controller', __name__)

@controller.route('/api/app/access_points', methods=["GET"])
def access_points():
  delegate: Callable = wiz_globals.access_point_delegate
  if delegate:
    access_point_list = delegate()
    return jsonify(data=access_point_list)
  else:
    return jsonify(data=[])



@controller.route('/api/app/workload_versions', methods=["GET"])
def workload_versions():
  ns = wiz_globals.ns
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
