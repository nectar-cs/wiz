# noinspection PyUnresolvedReferences
import dotenv


# noinspection PyUnresolvedReferences


def start():
  from k8kat.res.rbac.rbac import KatClusterRole, KatRole, \
    KatClusterRoleBinding, KatRoleBinding
  # noinspection PyUnresolvedReferences
  from k8kat.res.pod.kat_pod import KatPod
  # noinspection PyUnresolvedReferences
  from k8kat.res.dep.kat_dep import KatDep
  # noinspection PyUnresolvedReferences
  # noinspection PyUnresolvedReferences
  from k8kat.auth.kube_broker import broker
  # noinspection PyUnresolvedReferences
  from k8kat.res.ns.kat_ns import KatNs

  from nectwiz.model.base import wiz_model
  from nectwiz.model.base.resource_selector import ResourceSelector
  from nectwiz.model.field.field import Field
  from nectwiz.model.operation.operation import Operation
  from nectwiz.model.action.actions.apply_manifest_action import ApplyManifestAction
  from nectwiz.model.predicate.predicate import Predicate
  from nectwiz.model.operation.stage import Stage
  from nectwiz.model.operation.step import Step


  print("[nectwiz::shell] loaded packages for shell mode")
