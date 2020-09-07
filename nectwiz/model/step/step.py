from typing import List, Dict, Union, Tuple, Optional

from nectwiz.core.core import config_man, utils
from nectwiz.core.job import job_client
from nectwiz.model.operations.operation_state import OperationState
from nectwiz.model.step.step_state import StepState
from nectwiz.core.core.types import CommitOutcome, StepCommitActionKwargs
from nectwiz.model.action.action import Action
from nectwiz.model.base.res_match_rule import ResMatchRule
from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.field.field import Field, TARGET_CHART, TARGET_STATE, TARGET_INLINE, TARGET_TYPES
from nectwiz.model.step import step_exprs, status_computer
from nectwiz.model.step.step_exprs import parse_recalled_state

TOS = OperationState
TSS = StepState
TOOS = Optional[OperationState]
TCO = CommitOutcome


class Step(WizModel):

  @property
  def field_keys(self):
    """
    Getter for the Fields associated with a Step.
    :return:
    """
    return self.config.get('fields', [])

  def sig(self):
    return f"{self.parent.id()}::{self.id()}"

  def updates_chart(self) -> bool:
    """
    Decides whether the chart needs to be updated. First looks at "updates_chart"
    variable, then at whether there are any chart fields associated with the step.
    :return: True if needs to be update, False otherwise.
    """
    if 'updates_chart' in self.config.keys():
      return self.config.get('updates_chart', True)
    else:
      manifest_fields = filter(Field.is_chart_var, self.fields())
      return len(list(manifest_fields)) > 0

  def applies_manifest(self) -> bool:
    """
    Decides whether to kubectl apply the manifest at this time.
    :return: True if yes, False otherwise.
    """
    if 'applies_manifest' in self.config.keys():
      return self.config.get('applies_manifest', True)
    else:
      return len(self.res_selectors()) > 0

  def triggers_action(self) -> bool:
    """
    Checks if there is at least one associated job.
    :return: True if yes, False otherwise.
    """
    return self.applies_manifest() or bool(self.action())

  def action(self):
    return 3

  @property
  def res_selector_descs(self) -> List[Union[str, dict]]:
    """
    Getter for resource selector descriptors. Returns [] if unspecified.
    Resource selectors (resource_apply_filter) specify the resources that a
    particular step affects when committed.
    :return: resource_apply_filter in list form.
    """
    raw_descriptor = self.config.get('resource_apply_filter')
    if raw_descriptor is not None:
      is_list = type(raw_descriptor) == list
      return raw_descriptor if is_list else [raw_descriptor]
    else:
      return []

  @property
  def next_step_descriptor(self) -> Union[Dict, str]:
    """
    Getter for the next Step's descriptor.
    :return: next Steps' descriptor.
    """
    return self.config.get('next')

  @property
  def job_descriptor(self) -> Dict:
    """
    Getter for the Step's job descriptor
    :return: job descriptor.
    """
    return self.config.get('job', {})

  def next_step_id(self, values: Dict[str, str]) -> str:
    """
    Returns the id of the next step, be it explicit or an if-then-else type step.
    :param values: if-then-else values, if necessary.
    :return: string containing next step.
    """
    root = self.next_step_descriptor
    return step_exprs.eval_next_expr(root, values)

  def has_explicit_next(self) -> bool:
    """
    Checks if the current step has an explicit next step.
    :return: True if it does, otherwise False.
    """
    return not step_exprs.is_default_next(self.next_step_descriptor)

  def fields(self) -> List[Field]:
    """
    Loads the Fields associated with the Step.
    :return: List of Field instances.
    """
    return self.load_children('fields', Field)

  def field(self, key) -> Field:
    """
    Finds the Field by key and inflates (instantiates) into a Field instance.
    :param key: identifier for desired Field.
    :return: Field instance.
    """
    return self.load_list_child('fields', Field, key)

  def sanitize_field_assigns(self, values: Dict[str, any]) -> dict:
    """
    Converts the values in the passed key-value dict from strings to sanitized
    instances of the Fields class.
    :param values: dict to be sanitized.
    :return: sanitized key-values dict.
    """
    transform = lambda k: self.field(k).sanitize_value(values[k])
    return {key: transform(key) for key, value in values.items()}

  def res_selectors(self) -> List[ResMatchRule]:
    """
    Retrieves resource selectors and converts to instances of the ResMatchRule
    class.
    :return: list of ResMatchRule instances.
    """
    return list(map(ResMatchRule, self.res_selector_descs))

  def compute_recalled_assigns(self, target: str, prev_state: TSS) -> dict:
    """
    Collects all the state assigns of target type, then filters them by
    included/excluded tag.

    items inside descriptors are of the format: {
      target = chart,
      included_keys = [1,2,3],
      excluded_key = [4,5,6]
    }
    :param target: type of state_assigns to collect, eg "chart" or "inline".
    :param prev_state: for which OperationState to collect.
    :return: dict with included state_assigns.
    """
    # Step 1- get matching state_recalls
    predicate = lambda d: d.get('target', 'chart') == target
    descriptors = filter(predicate, self.config.get('state_recalls', []))
    state_assigns = prev_state.state_assigns
    # Step 2 - get included - excluded keys for those state_recalls
    gather_keys = lambda d: parse_recalled_state(d, state_assigns.keys())
    recalled_keys = utils.flatten(map(gather_keys, descriptors))
    # Step 3 - produce a key-value dict for keys that are left
    return {key: state_assigns.get(key) for key in recalled_keys}

  # noinspection PyUnusedLocal
  def finalize_chart_values(self, assigns: Dict, all_assigns, prev_state: TSS) -> dict:
    """
    Merges existing chart assigns with new ones from the Front End and sanitizes both.
    Called by the partition function via reflection.
    :param assigns: ultimately come from request.json['values']
    :param all_assigns: todo don't seem to be used?
    :param prev_state: OperationState for which to compute chart assigns.
    :return: updated and sanitized dict with chart assigns.
    """
    recalled_from_state = self.compute_recalled_assigns('chart', prev_state)
    return self.sanitize_field_assigns({**recalled_from_state, **assigns})

  # noinspection PyUnusedLocal
  def finalize_inline_values(self, assigns: Dict, all_assigns, prev_state: TSS) -> dict:
    """
    Merges existing inline assigns with new ones from the Front End and sanitizes both.
    Called by the partition function via reflection.
    :param assigns: ultimately come from request.json['values']
    :param all_assigns: todo don't seem to be used?
    :param prev_state: OperationState for which to compute inline assigns.
    :return: updated and sanitized dict with inline assigns.
    """
    recalled_from_state = self.compute_recalled_assigns('inline', prev_state)
    return self.sanitize_field_assigns({**recalled_from_state, **assigns})

  # noinspection PyUnusedLocal
  def finalize_state_values(self, assigns: Dict, all_assigns, op_state: TOS) -> dict:
    """
    Sanitizes state assigns retrieved from the Front End.
    Called by the partition function via reflection.
    :param assigns: ultimately come from request.json['values']
    :param all_assigns: todo don't seem to be used?
    :param op_state: OperationState for which to compute state assigns.
    :return: sanitized dict with state assigns.
    """
    return self.sanitize_field_assigns(assigns)

  def find_commit_status(self, op_state):
    pass


  def run(self, assigns: Dict, prev_state: StepState):
    """
    Commits a step, which involves:
      1. Partitioning assigns into chart/inline/state + merging with existing
      2. For chart/state assigns: inserting into CommitOutcome
      3. For chart assigns only: inserting into the ConfigMap
      4. For inline assigns: kubectl applying
      5. Creating and starting any associated jobs

    :param assigns: new assigns to be committed.
    :param prev_state: needed to merge with existing assigns for all 3 buckets
    :return: CommitOutcome, a dict containing chart/state assigns as well as logs
    from applying inline assigns and job_id for any generated jobs.
    """
    op_state: OperationState = prev_state.parent_op()

    final_assigns = self.partition_user_asgs(assigns, op_state)
    chart_asg, inline_asg, state_asg = final_assigns

    if len(chart_asg):
      keyed_tuples = list(chart_asg.items())
      config_man.commit_keyed_tam_assigns(keyed_tuples)

    if self.triggers_action():
      action_kwargs = self.g_action_kwargs(chart_asg, inline_asg, state_asg)
      action_cls = self.load_child(Action, 'action').__class__
      job_id = job_client.enqueue_action(action_cls, **action_kwargs)
      prev_state.notify_action_started(job_id)
    else:
      prev_state.notify_succeeded()

  def g_action_kwargs(self, chart, inline, state) -> StepCommitActionKwargs:
    return StepCommitActionKwargs(
      inline_assigns=inline,
      chart_assigns=chart,
      state_assigns=state,
      res_selector_descs=self.res_selector_descs
    )

  def compute_status(self, prev_state: TSS = None) -> bool:
    if prev_state.was_running():
      parallel_job = job_client.find_job(prev_state.job_id)
      if parallel_job.is_finished:
        prev_state.notify_is_verifying()
        return self.compute_status_verifying(prev_state)
      else:
        print("Job still running")
        return False

    elif prev_state.was_verifying():
      status_computer.compute_status(self.config.get('exit'), prev_state)
      return self.compute_status_verifying(prev_state)

  def compute_status_verifying(self, prev_state):
    status_computer.compute_status(self.config.get('exit'), prev_state)
    return True

  def flags(self):
    """
    Appends appropriate flags to the Step's config. The 2 options are:
      1. Applies manifest: do we apply the manifest at this step?
      2. Job running: do we run any jobs at this step?
    :return: list of set flags.
    """
    _flags: List[str] = self.config.get('flags', [])
    if self.applies_manifest():
      _flags.append('manifest_applying')
    if self.triggers_action():
      _flags.append('job_running')
    return list(set(_flags))

  def partition_user_asgs(self, assigns, op_state: TOS) -> Tuple:
    """
    Partitions new assigns into 3 buckets (chart, inline, state) and
    merges with existing assigns in each bucket.
    :param assigns: new assigns to be partitioned.
    :param op_state: state from which to collect existing assigns.
    :return: tuple of all chart assigns, partitioned and merged.
    """
    buckets = {target_type: {} for target_type in TARGET_TYPES}

    for key, value in assigns.items():
      field = next((f for f in self.fields() if f.key == key), None)
      if field:
        buckets[field.target][key] = value

    for target_type in TARGET_TYPES:
      finalizer = bucket_finalizer_mapping(target_type, self)
      # noinspection PyArgumentList
      buckets[target_type] = finalizer(buckets[target_type], assigns, op_state)

    return tuple(buckets[target_type] for target_type in TARGET_TYPES)


def bucket_finalizer_mapping(key, obj: Step):
  """
  Maps the finalizer methods to possible targets.
  :param key: possible target.
  :param obj: Step object, owner of the finalizer method.
  :return: finalizer method.
  """
  if key == TARGET_CHART:
    return obj.finalize_chart_values
  elif key == TARGET_INLINE:
    return obj.finalize_inline_values
  elif key == TARGET_STATE:
    return obj.finalize_state_values
  else:
    print("DANGER UNKNOWN ASSIGNMENT TARGET " + key)
