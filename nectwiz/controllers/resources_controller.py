from flask import Blueprint, jsonify
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


@controller.route(f'{BASE_PATH}/<kind>/<name>')
def resource_detail(kind: str, name: str):
  """
  Finds a particular KatRes resource instance.
  :param kind: kind of resource, eg KatDep.
  :param name: name of resource.
  :return: serialized resource KatRes instance.
  """
  kat_class = KatRes.class_for(kind)
  res = kat_class.find(name, config_man.ns())
  serializer = kind_serializer_mapping.get(kind)
  serialized = serializer(res) if res and serializer else None
  return jsonify(data=serialized)


kind_serializer_mapping = dict(
  deployment=res_serializers.deployment,
  resource_quota=res_serializers.resource_quota,
  role=res_serializers.role
)
