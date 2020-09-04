from typing import Type, List

from flask import Blueprint, jsonify

from k8kat.res.base.kat_res import KatRes
from k8kat.res.config_map.kat_map import KatMap
from k8kat.res.dep.kat_dep import KatDep
from k8kat.res.ingress.kat_ingress import KatIngress
from k8kat.res.pvc.kat_pvc import KatPvc
from k8kat.res.quotas.kat_quota import KatQuota
from k8kat.res.rbac.rbac import KatRole, KatRoleBinding
from k8kat.res.sa.kat_service_account import KatServiceAccount
from k8kat.res.secret.kat_secret import KatSecret
from k8kat.res.svc.kat_svc import KatSvc
from nectwiz.core.wiz_app import wiz_app
from nectwiz.serializers import res_serializers

controller = Blueprint('resources_controller', __name__)

BASE_PATH = '/api/resources'


@controller.route(f'{BASE_PATH}/category/<category_id>', methods=['GET'])
def list_by_category(category_id):
  """
  Lists KatRes resources by category.
  :param category_id: eg "workloads" would list KatDep resources.
  :return: list of serialized KatRes instances.
  """
  kat_res_classes: List[Type[KatRes]] = category_mapping[category_id]
  all_serialized_res = []
  for kat_class in kat_res_classes:
    res_instances = kat_class.list_excluding_sys(ns=wiz_app.ns())
    serialized = [res_serializers.basic(res) for res in res_instances]
    all_serialized_res += serialized
  return jsonify(data=all_serialized_res)


@controller.route(f'{BASE_PATH}/<kind>/<name>', methods=['GET'])
def resource_detail(kind: str, name: str):
  """
  Finds a particular KatRes resource instance.
  :param kind: kind of resource, eg KatDep.
  :param name: name of resource.
  :return: serialized resource KatRes instance.
  """
  kat_class = KatRes.find_res_class(kind)
  res = kat_class.find(name, wiz_app.ns())
  serializer = kind_serializer_mapping.get(kind)
  serialized = serializer(res) if res and serializer else None
  return jsonify(data=serialized)


kind_serializer_mapping = dict(
  deployment=res_serializers.deployment,
  resource_quota=res_serializers.resource_quota,
  role=res_serializers.role
)


category_mapping = dict(
  workloads=[KatDep],
  network=[KatSvc, KatIngress],
  policy=[KatRole, KatRoleBinding, KatQuota, KatServiceAccount],
  config=[KatMap, KatSecret],
  other=[KatPvc]
)
