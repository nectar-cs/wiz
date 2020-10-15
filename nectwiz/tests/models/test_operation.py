# from typing import Type
#
# from nectwiz.model.action.actions.apply_manifest_action import ApplyManifestAction
# from nectwiz.model.base.wiz_model import WizModel
# from nectwiz.model.operation.operation import Operation
# from nectwiz.model.operation.operation_state import OperationState
# from nectwiz.tests.models.test_wiz_model import Base
#
#
# class TestOperation(Base.TestWizModel):
#
#   @classmethod
#   def model_class(cls) -> Type[WizModel]:
#     return Operation
#
#   def test_serialize_telem(self):
#     uuid = OperationState.gen(operation.id())
#
#     pass
#
#
# operation = Operation(dict(
#   id='test-op',
#   stages=[
#     dict(
#       id='test-stage',
#       steps=[
#         dict(
#           id='test-step',
#           action=ApplyManifestAction.__name__,
#           fields=[
#             dict(
#               id='foo',
#               target='chart'
#             )
#           ]
#         )
#       ]
#     )
#   ]
# ))
#
#
#
