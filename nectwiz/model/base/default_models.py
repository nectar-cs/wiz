def default_model_classes():
  from nectwiz.model.action.actions.cmd_exec_action import CmdExecAction
  from nectwiz.model.action.actions.apply_manifest_action import ApplyManifestAction
  from nectwiz.model.adapters.deletion_spec import DeletionSpec
  from nectwiz.model.variable.manifest_variable import ManifestVariable
  from nectwiz.model.input.generic_input import GenericInput
  from nectwiz.model.input.slider_input import SliderInput
  from nectwiz.model.adapters.list_resources_adapter import ResourceQueryAdapter
  from nectwiz.model.operation.operation import Operation
  from nectwiz.model.operation.stage import Stage
  from nectwiz.model.operation.step import Step
  from nectwiz.model.operation.field import Field
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
  from nectwiz.model.predicate.common_predicates import TruePredicate
  from nectwiz.core.telem.updates_man import UpdateAction
  from nectwiz.model.action.actions.backup_config_action import BackupConfigAction
  from nectwiz.model.action.actions.backup_config_action import UpdateLastCheckedAction
  from nectwiz.core.telem.updates_man import WizUpdateAction
  from nectwiz.model.adapters.app_status_computer import AppStatusComputer
  from nectwiz.model.stats.prometheus_single_value_computer import PrometheusScalarComputer

  from nectwiz.model.stats.prometheus_computer import PrometheusComputer
  from nectwiz.model.stats.metrics_computer import MetricsComputer
  from nectwiz.model.stats.prometheus_series_computer import PrometheusSeriesComputer
  from nectwiz.model.stats.basic_resource_metrics_computer import BasicResourceMetricsComputer

  from nectwiz.model.predicate.iftt import Iftt
  from nectwiz.model.predicate.common_predicates import FalsePredicate
  from nectwiz.model.hook.hook import Hook
  from nectwiz.model.supply.value_supplier import ValueSupplier
  from nectwiz.model.supply.http_data_supplier import HttpDataSupplier
  from nectwiz.model.supply.resources_supplier import ResourcesSupplier
  from nectwiz.model.predicate.system_check import SystemCheck
  from nectwiz.model.supply.unit_supplier import UnitSupplier
  from nectwiz.model.input.checkboxes_input import SelectInput
  from nectwiz.model.input.select_option import InputOption
  from nectwiz.model.adapters.app_endpoints_adapter import AccessPointAdapter
  from nectwiz.model.adapters.app_endpoints_adapter import AccessPointsProvider

  from nectwiz.model.supply.random_string_supplier import RandomStringSupplier
  return [
    Operation,
    Stage,
    Step,
    Field,
    Hook,

    GenericVariable,
    ManifestVariable,
    VariableValueDecorator,
    FixedReplicasDecorator,

    ErrorHandler,
    ErrorTriggerSelector,
    ErrorDiagnosis,
    DiagnosisActionable,

    GenericInput,
    SliderInput,
    SelectInput,
    CheckboxesInput,
    CheckboxInput,
    InputOption,

    ResourceSelector,
    FormatPredicate,
    MultiPredicate,
    TruePredicate,
    FalsePredicate,

    Iftt,
    ValueSupplier,
    HttpDataSupplier,
    ResourcesSupplier,
    UnitSupplier,
    RandomStringSupplier,

    AppStatusComputer,
    SystemCheck,
    AccessPointsProvider,
    AccessPointAdapter,

    MultiAction,
    CmdExecAction,
    ApplyManifestAction,
    DeleteResourcesAction,
    RunPredicatesAction,
    UpdateAction,
    BackupConfigAction,
    UpdateLastCheckedAction,
    WizUpdateAction,

    ResourceQueryAdapter,
    DeletionSpec,
    PrometheusComputer,
    MetricsComputer,
    PrometheusScalarComputer,
    PrometheusSeriesComputer,
    BasicResourceMetricsComputer,

    OperationRunSimulator
  ]
