from typing import Dict

from werkzeug.utils import cached_property

from nectwiz.core.core import updates_man, consts
from nectwiz.core.core.config_man import config_man
from nectwiz.core.core.types import ProgressItem, UpdateDict
from nectwiz.core.core.utils import deep_merge
from nectwiz.model.action.action_parts.apply_manifest_action_part import ApplyManifestActionPart
from nectwiz.model.action.action_parts.await_predicates_settle_action_part import AwaitPredicatesSettleActionPart
from nectwiz.model.action.base.action import Action
from nectwiz.model.action.base.observer import simple_action_eval
from nectwiz.model.factory.predicate_factories import PredicateFactory

key_patch_tam = 'patch_tam'
key_replace_defaults = 'replace_defaults'


class ApplyUpdateAction(Action):
  KEY_UPDATE_ID = 'update_id'

  def __init__(self, config: Dict):
    super().__init__(config)
    self.observer.progress = ProgressItem(
      id=f'apply_update',
      status='running',
      info=f"Updates default values, re-applies manifest",
      sub_items=[
        ProgressItem(
          id=key_patch_tam,
          status='idle',
          title='Commit TAM with new version/type',
          info="Patch master ConfigMap entry for TAM definition",
        ),
        ProgressItem(
          id=key_replace_defaults,
          status='idle',
          title='Update manifest variable defaults',
          info='Load defaults from new TAM, commit them to master ConfigMap'
        )
      ]
    )

  @cached_property
  def update(self) -> UpdateDict:
    update_id = self.get_prop(self.KEY_UPDATE_ID)
    return updates_man.fetch_update(update_id)

  @cached_property
  def store_telem(self) -> bool:
    return True

  @cached_property
  def event_type(self) -> str:
    return 'apply_update'

  def perform(self, **kwargs) -> bool:
    with simple_action_eval(self.observer, key_patch_tam):
      updates_man.commit_new_tam(self.update)

    with simple_action_eval(self.observer, key_replace_defaults):
      updates_man.commit_new_defaults(self.update)

    outcomes = ApplyManifestActionPart.perform(
      tam=config_man.tam(),
      values=self.manifest_bound_values(),
      observer=self.observer,
      selectors=[]
    )

    AwaitPredicatesSettleActionPart.perform(
      self.observer,
      PredicateFactory.from_apply_outcome(outcomes)
    )

    self.observer.on_succeeded()
    return True

  def manifest_bound_values(self) -> Dict:
    suppliers = consts.TAM_VALUE_SOURCES
    value_bundles = [self.resolve_prop_value(s) for s in suppliers]
    return deep_merge(*value_bundles)
