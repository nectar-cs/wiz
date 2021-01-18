from typing import Optional

from werkzeug.utils import cached_property

from nectwiz.core.core import updates_man, hub_api_client
from nectwiz.core.core.config_man import config_man
from nectwiz.core.core.types import ProgressItem, InjectionDesc
from nectwiz.model.action.action_parts.apply_manifest_action_part import ApplyManifestActionPart
from nectwiz.model.action.action_parts.await_predicates_settle_action_part import AwaitPredicatesSettleActionPart
from nectwiz.model.action.base.action import Action
from nectwiz.model.action.base.observer import simple_action_eval
from nectwiz.model.adapters.injection_orchestrator import InjectionOrchestrator
from nectwiz.model.factory.predicate_factories import PredicateFactory


class SyncInjectionsAction(Action):

  def __init__(self, config):
    super().__init__(config)
    self.observer.progress = ProgressItem(
      id='apply_manifest',
      status='running',
      title="Apply Resources",
      info="Updates the manifest and waits for a settled state",
      sub_items=[
        ProgressItem(
          id=fetch_part_key,
          status='idle',
          title='Load Templated Manifest',
          info=f"Creates a pod loaded with the vendor manifest image",
          sub_items=[]
        ),
        ProgressItem(
          id=update_vars_part_key,
          status='idle',
          title='Run kubectl apply',
          info='Applies the templated manifest to the cluster',
          data={},
          sub_items=[]
        ),
        *ApplyManifestActionPart.progress_items(),
        *AwaitPredicatesSettleActionPart.progress_items()
      ]
    )

  @cached_property
  def orchestrator(self) -> InjectionOrchestrator:
    return InjectionOrchestrator.inflate_singleton()

  def perform(self) -> bool:
    with simple_action_eval(self.observer, fetch_part_key):
      bundle: InjectionDesc = updates_man.latest_injection_bundle()
      self.raise_on_bundle_na(bundle)

    with simple_action_eval(self.observer, update_vars_part_key):
      config_man.patch_manifest_defaults(bundle['chart'])

    if len(bundle['inlines']) > 0:
      outcomes = ApplyManifestActionPart.perform(
        tam=None,
        values=bundle['inlines'],
        observer=self.observer,
        selectors=self.orchestrator.apply_selectors
      )

      AwaitPredicatesSettleActionPart.perform(
        self.observer,
        PredicateFactory.from_apply_outcome(outcomes)
      )
    return True

  def raise_on_bundle_na(self, injection_bundle: Optional[InjectionDesc]):
    if not injection_bundle:
      host = hub_api_client.backend_host()
      self.observer.process_error(
        fatal=True,
        tone='error',
        reason=f"Negative response from Nectar API ({host})"
      )


fetch_part_key = 'fetch-injections'
update_vars_part_key = 'update_vars'
