from typing import Type, List

from flask import Blueprint, jsonify
from k8_kat.res.base.kat_res import KatRes
from k8_kat.res.rs.kat_rs import KatRs

from k8_kat.res.sa.kat_service_account import KatServiceAccount

from k8_kat.res.pvc.kat_pvc import KatPvc

from k8_kat.res.secret.kat_secret import KatSecret

from k8_kat.res.config_map.kat_map import KatMap

from k8_kat.res.quotas.kat_quota import KatQuota

from k8_kat.res.rbac.rbac import KatRole, KatRoleBinding

from k8_kat.res.ingress.kat_ingress import KatIngress

from k8_kat.res.svc.kat_svc import KatSvc

from k8_kat.res.dep.kat_dep import KatDep
from wiz.core.wiz_globals import wiz_app
from wiz.serializers.resources import res_serializers

controller = Blueprint('resources_controller', __name__)

BASE_PATH = '/api/resources'


@controller.route(f'{BASE_PATH}/category/<category_id>', methods=['GET'])
def list_by_category(category_id):
  kat_res_classes: List[Type[KatRes]] = category_mapping[category_id]
  all_serialized_res = []
  for kat_class in kat_res_classes:
    res_instances = kat_class.list_excluding_sys(ns=wiz_app.ns)
    serialized = [res_serializers.basic(res) for res in res_instances]
    all_serialized_res += serialized
  return jsonify(data=all_serialized_res)


category_mapping = dict(
  workloads=[KatDep],
  network=[KatSvc, KatIngress],
  policy=[KatRole, KatRoleBinding, KatQuota, KatServiceAccount],
  config=[KatMap, KatSecret],
  other=[KatPvc]
)
