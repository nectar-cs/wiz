import dotenv




from k8kat.res.rbac.rbac import KatClusterRole, KatRole, \
  KatClusterRoleBinding, KatRoleBinding
from k8kat.res.pod.kat_pod import KatPod
from k8kat.res.dep.kat_dep import KatDep
from k8kat.res.node.kat_node import KatNode
from k8kat.auth.kube_broker import broker
from k8kat.res.ns.kat_ns import KatNs

from nectwiz.core.core import prom_api_client
from nectwiz.model.base import wiz_model
from nectwiz.model.base.resource_selector import ResourceSelector
from nectwiz.model.base.wiz_model import models_man
from nectwiz.model.field.field import Field
from nectwiz.model.operation.operation import Operation
from nectwiz.model.action.actions.apply_manifest_action import ApplyManifestAction
from nectwiz.model.predicate.predicate import Predicate
from nectwiz.model.operation.stage import Stage
from nectwiz.model.stats.basic_resource_metrics_computer import BasicResourceMetricsComputer
from nectwiz.model.stats.prometheus_computer import PrometheusComputer
from nectwiz.model.operation.step import Step

from nectwiz.model.action.actions.cmd_exec_action import CmdExecAction
from nectwiz.model.action.actions.apply_manifest_action import ApplyManifestAction
from nectwiz.model.action.actions.flush_telem_action import FlushTelemAction
from nectwiz.model.adapters.deletion_spec import DeletionSpec
from nectwiz.model.stats.prometheus_series_computer import PrometheusSeriesComputer
from nectwiz.model.stats.prometheus_single_value_computer import PrometheusScalarComputer
from nectwiz.model.variable.manifest_variable import ManifestVariable
from nectwiz.model.input.input import GenericInput
from nectwiz.model.input.select_input import SelectInput
from nectwiz.model.input.slider_input import SliderInput
from nectwiz.model.adapters.list_resources_adapter import ResourceQueryAdapter
from nectwiz.model.operation.operation import Operation
from nectwiz.model.operation.stage import Stage
from nectwiz.model.operation.step import Step
from nectwiz.model.field.field import Field
from nectwiz.model.variable.generic_variable import GenericVariable
from nectwiz.model.base.resource_selector import ResourceSelector
from nectwiz.model.operation.operation_run_simulator import OperationRunSimulator
from nectwiz.model.action.actions.delete_resources_action import DeleteResourcesAction
from nectwiz.model.action.actions.multi_action import MultiAction
from nectwiz.model.action.actions.run_predicates_action import RunPredicatesAction
from nectwiz.model.input.checkboxes_input import CheckboxesInput
from nectwiz.model.input.checkboxes_input import CheckboxInput
from nectwiz.model.variable.variable_value_decorator import VariableValueDecorator
from nectwiz.model.variable.pod_scaling_decorator import FixedReplicasDecorator
from nectwiz.model.error.error_handler import ErrorHandler
from nectwiz.model.error.error_trigger_selector import ErrorTriggerSelector
from nectwiz.model.error.error_diagnosis import ErrorDiagnosis
from nectwiz.model.error.diagnosis_actionable import DiagnosisActionable
from nectwiz.model.predicate.format_predicate import FormatPredicate
from nectwiz.model.predicate.multi_predicate import MultiPredicate

broker.connect(dict(
  auth_type='kube-config',
  context='wear'
))

models_man.add_defaults()

print("[nectwiz::shell] loaded packages for shell mode")