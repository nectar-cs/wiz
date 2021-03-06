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
    self.assertEqual("Pod", selector.res_kind)
    self.assertEqual("nginx", selector.res_name)

  def test_selects_res(self):
    res = dict(
      kind='Pod',
      metadata=dict(
        namespace='foo',
        name='bar',
        labels=dict(
          app='nectar',
          tier='testware'
        )
      ),
      spec=dict(
        replicas=2,
        imagePullPolicy='Never'
      )
    )

    selector = ResourceSelector(dict(
      res_kind='NotPod',
      label_selector=dict(
        app='nectar'
      )
    ))
    self.assertFalse(selector.selects_res(res))

    selector = ResourceSelector(dict(
      res_kind='*',
      label_selector=dict(
        app='nectar'
      )
    ))
    self.assertTrue(selector.selects_res(res))

    selector = ResourceSelector(dict(
      res_kind='Pod',
      label_selector=dict(
        app='nectar'
      )
    ))
    self.assertTrue(selector.selects_res(res))

    selector = ResourceSelector(dict(
      res_kind='Pod',
      label_selector=dict(
        app='nectar',
        tier='backend'
      )
    ))
    self.assertFalse(selector.selects_res(res))

    selector = ResourceSelector(dict(
      res_kind='Pod',
      label_selector=dict(
        app='nectar',
        tier='testware'
      ),
      field_selector={
        'spec.imagePullPolicy': 'Never'
      }
    ))
    self.assertTrue(selector.selects_res(res))

    selector = ResourceSelector(dict(
      res_kind='Pod',
      label_selector=dict(
        app='nectar',
        tier='testware'
      ),
      field_selector={
        'spec.imagePullPolicy': 'Never',
        'metadata.namespace': 'baz'
      }
    ))
    self.assertFalse(selector.selects_res(res))

  def test_build_k8kat_query(self):
    config_man._ns = 'irrelevant'
    selector_config = dict(
      name='nginx:{version}',
      label_selector=dict(
        app='nectar-{flavor}'
      ),
      field_selector={
        'metadata.uuid': '{secrets/123}'
      }
    )

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
      ),
      not_labels={}
    )

    selector = ResourceSelector.inflate(
      selector_config,
      patches=dict(context=context)
    )

    actual = selector.build_k8kat_query()
    self.assertEqual(expect, actual)
