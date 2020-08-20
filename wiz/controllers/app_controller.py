from typing import List

from flask import Blueprint, jsonify

from k8_kat.res.dep.kat_dep import KatDep

from wiz.core import update_manager
from wiz.core.wiz_app import wiz_app
from wiz.model.adapters.app_endpoint_adapter import AppEndpointAdapter
from wiz.model.adapters.base_consumption_adapter import BaseConsumptionAdapter

controller = Blueprint('app_controller', __name__)

BASE_PATH = '/api/app'


@controller.route(f'{BASE_PATH}/check-for-updates')
def app_check_updates():
  update = update_manager.fetch_next_update()
  return jsonify(data=update)


@controller.route(f'{BASE_PATH}/apply-updates')
def app_apply_updates():
  pass


@controller.route(f'{BASE_PATH}/resource-stats', methods=["GET"])
def app_resource_usage():
  """
  Returns the Base Consumption adapter.
  :return: serialized adapter object.
  """
  adapter = wiz_app.find_adapter_subclass(BaseConsumptionAdapter, True)
  output = adapter().serialize()
  return jsonify(data=output)


@controller.route(f'{BASE_PATH}/application_endpoints', methods=["GET"])
def application_endpoints():
  """
  Returns a list of application endpoint adapters.
  :return: list of serialized adapters.
  """
  provider = wiz_app.find_provider(AppEndpointAdapter)()
  if provider:
    adapters = provider.produce_adapters()
    ser_endpoints = [a.serialize() for a in adapters]
    return jsonify(data=ser_endpoints)
  else:
    return jsonify(data=[])


@controller.route(f'{BASE_PATH}/workload_versions', methods=["GET"])
def workload_versions():
  """
  Returns the versions and last update times for workloads.
  :return: list with versions and last updates times for each workload.
  """
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
