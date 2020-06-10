import dotenv

from sample_wiz.adapters import app_endpoints
from sample_wiz.overrides import fields, steps
from wiz import server
from wiz.core import utils
from wiz.core.wiz_globals import wiz_app

yamls_base = 'sample_wiz/operation-yamls'

wiz_app.add_configs(
  utils.yamls_in_dir(f'{yamls_base}/installation') +
  utils.yamls_in_dir(f'{yamls_base}/move-to-own-pvc') +
  utils.yamls_in_dir(f'{yamls_base}/variables')
)

wiz_app.add_overrides([
  fields.DbPasswordField,
  fields.SecKeyBaseField,
  fields.AttrEncField,
  steps.LocateExternalDatabaseStep,
  steps.AvailabilityStep
])

wiz_app.add_providers([
  app_endpoints.AppEndpointsProvider
])

dotenv.load_dotenv()
server.start()
