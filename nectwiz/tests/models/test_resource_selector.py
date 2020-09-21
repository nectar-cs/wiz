from typing import Type

from nectwiz.core.core.config_man import config_man
from nectwiz.model.base.resource_selector import ResourceSelector
from nectwiz.model.base.wiz_model import WizModel
from nectwiz.tests.models.test_wiz_model import Base


class TestResourceSelector(Base.TestWizModel):
  @classmethod
  def model_class(cls) -> Type[WizModel]:
    return ResourceSelector

  def test_inflate_with_expr(self):
    selector: ResourceSelector = ResourceSelector.inflate("Pod:nginx")
    self.assertEqual("Pod", selector.k8s_kind)
    self.assertEqual("nginx", selector.name)

  def test_build_k8kat_query(self):
    config_man._ns = 'irrelevant'
    selector = ResourceSelector(dict(
      name='nginx:{version}',
      label_selector=dict(
        app='nectar-{flavor}'
      ),
      field_selector={
        'metadata.uuid': '{secrets/123}'
      }
    ))

    context = dict(
      version='3.2.1',
      flavor='peach',
      resolvers=dict(
        secrets=lambda k: f"{k}_uuid"
      )
    )

    expect = dict(
      ns='irrelevant',
      fields={
        'metadata.name': 'nginx:3.2.1',
        'metadata.uuid': '123_uuid'
      },
      labels=dict(
        app='nectar-peach'
      )
    )

    actual = selector.build_k8kat_query(context)
    self.assertEqual(expect, actual)
