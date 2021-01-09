# class UpdateAction(Action):
#   def __init__(self, config: Dict):
#     super().__init__(config)
#     self.store_telem = True
#     self.update: UpdateDict = config.get('update')
#     self.event_type = 'app_update'
#     self.observer.progress = ProgressItem(
#       id='app-update-action',
#       status='running',
#       info="Updates the variable manifest and waits for a settled state",
#       sub_items=[
#         *UpdateManifestDefaultsActionPart.progress_items(),
#         *ApplyManifestActionPart.progress_items(),
#         *AwaitPredicatesSettleActionPart.progress_items(),
#       ]
#     )
#
#   def telem_extras(self):
#     return dict(
#       **super().telem_extras(),
#       **self.update
#     )
#
#   def perform(self, **config):
#     self.update: UpdateDict = config.get('update')
#     update = self.update
#     self.event_name = f"{update.get('type')}:{update.get('version')}"
#
#     before_hooks = find_hooks('before', update['type'])
#     after_hooks = find_hooks('after', update['type'])
#     progress_items = self.observer.progress['sub_items']
#
#     self.observer.progress['sub_items'] = (
#       RunHookGroupActionPart.progress_items('before', before_hooks) +
#       progress_items +
#       RunHookGroupActionPart.progress_items('after', after_hooks)
#     )
#
#     RunHookGroupActionPart.perform(
#       self.observer,
#       before_hooks
#     )
#
#     UpdateManifestDefaultsActionPart.perform(
#       self.observer,
#       update
#     )
#
#     outcomes = ApplyManifestActionPart.perform(
#       observer=self.observer
#     )
#
#     AwaitPredicatesSettleActionPart.perform(
#       self.observer,
#       PredicateFactory.from_apply_outcome(outcomes)
#     )
#
#     RunHookGroupActionPart.perform(
#       self.observer,
#       after_hooks
#     )
#
#     return True
#
