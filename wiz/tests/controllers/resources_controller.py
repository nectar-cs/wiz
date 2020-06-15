from flask import Blueprint
from k8_kat.res.dep.kat_dep import KatDep

controller = Blueprint('resources_controller', __name__)

BASE_PATH = '/api/resources'


@controller.route(f'{BASE_PATH}/workloads', methods=['GET'])
def list_workloads():
  deps = KatDep.list()


