import dotenv

from sample_wiz.adapters import app_endpoints
from sample_wiz.overrides import fields, steps
from wiz import server
from wiz.core import utils
from wiz.core.wiz_globals import wiz_app

wiz_app.add_configs(
  utils.yamls_in_dir('sample_wiz/yamls/installation') +
  utils.yamls_in_dir('sample_wiz/yamls/move-to-own-pvc') +
  utils.yamls_in_dir('sample_wiz/yamls/variables')
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
