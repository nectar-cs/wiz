from typing import Type

from flask import Blueprint, jsonify, request
from k8kat.res.base.kat_res import KatRes

from nectwiz.core.core.config_man import config_man
from nectwiz.model.adapters.list_resources_adapter import ResourceQueryAdapter
from nectwiz.serializers import res_serializers

controller = Blueprint('resources_controller', __name__)

BASE_PATH = '/api/resources'


@controller.route(f'{BASE_PATH}/category/<category_id>')
def resources_in_category(category_id):
  """
  Lists KatRes resources by category.
  :param category_id: eg "workloads" would list KatDep resources.
  :return: list of serialized KatRes instances.
  """
  key = 'nectar.adapters.resources-query-adapter'
  adapter: ResourceQueryAdapter = ResourceQueryAdapter.inflate(key)
  kats = adapter.query_in_category(category_id)
  serialized_kats = list(map(res_serializers.basic, kats))
  return jsonify(data=serialized_kats)

@controller.route(f'{BASE_PATH}/for_kinds')
def resources_for_kinds():
  """
  Finds a particular KatRes resource instance.
  :return: serialized resource KatRes instance.
  """
  kinds = request.args.get('kinds', '').split(',')
  kats = []
  for kind in list(set(kinds)):
    klass = KatRes.class_for(kind)
    kats += (klass.list(config_man.ns()) if klass else [])
  serialized_kats = list(map(res_serializers.basic, kats))
  return jsonify(data=serialized_kats)


@controller.route(f'{BASE_PATH}/detail/<kind>/<name>')
def resource_detail(kind: str, name: str):
  """
  Finds a particular KatRes resource instance.
  :param kind: kind of resource, eg KatDep.
  :param name: name of resource.
  :return: serialized resource KatRes instance.
  """
  kat_class: Type[KatRes] = KatRes.class_for(kind)
  res = kat_class.find(name, config_man.ns())
  serializer = kind_serializer_mapping.get(kat_class.kind)
  serialized = serializer(res) if res and serializer else None
  return jsonify(data=serialized)


kind_serializer_mapping = dict(
  Deployment=res_serializers.deployment,
  ResourceQuota=res_serializers.resource_quota,
  Role=res_serializers.role
)
