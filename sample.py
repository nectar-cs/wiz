import dotenv

from sample_wiz.adapters import app_endpoints
from sample_wiz.overrides import fields, steps
from wiz import server
from wiz.core import utils
from wiz.core.wiz_app import wiz_app


op_yamls_base = 'sample_wiz/operation-yamls'


wiz_app.add_configs(
  utils.yamls_in_dir(f'{op_yamls_base}/installation') +
  utils.yamls_in_dir(f'{op_yamls_base}/move-to-own-pvc') +
  utils.yamls_in_dir(f'{op_yamls_base}/easy-win') +
  utils.yamls_in_dir(f'sample_wiz/variables-yamls')
)


wiz_app.add_overrides([
  fields.DbPasswordField,
  fields.SecKeyBaseField,
  fields.AttrEncField,
  fields.CpuQuotaFields,
  fields.MemQuotaFields,
  steps.AvailabilityStep,
])


wiz_app.add_providers([
  app_endpoints.AppEndpointsProvider
])


wiz_app.app_name = 'hub-self-hosted'
wiz_app.ns = 'hub-self-hosted'
wiz_app.tami_name = 'gcr.io/nectar-bazaar/nectar-tedi:latest'
wiz_app.tami_args = '-e hub-self-hosted'


dotenv.load_dotenv()
server.start()
