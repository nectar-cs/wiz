import dotenv

from sample_wiz import sample_wiz
from wiz import server
from wiz.core import utils
from wiz.core.wiz_globals import wiz_app

wiz_app.add_configs(
  utils.yamls_in_dir('sample_wiz/installation') +
  utils.yamls_in_dir('sample_wiz/enable-ingress')
)

wiz_app.add_overrides([
  sample_wiz.LocateExternalDatabaseStep,
  sample_wiz.AvailabilityStep,
  sample_wiz.DbPasswordField,
  sample_wiz.SecKeyBaseField,
  sample_wiz.AttrEncField,
  sample_wiz.LocateExternalDatabaseStep,
  sample_wiz.AvailabilityStep
])

wiz_app.access_point_delegate = sample_wiz.access_points

# logging.basicConfig(level=logging.DEBUG)
dotenv.load_dotenv()
server.start()
