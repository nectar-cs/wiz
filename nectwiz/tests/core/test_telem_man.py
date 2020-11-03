from nectwiz.core.core.types import UpdateOutcome
from nectwiz.core.telem import telem_man
from nectwiz.tests.t_helpers.cluster_test import ClusterTest


class TestTelemMan(ClusterTest):

  def test_store_update_outcome(self):
    mock_outcome = UpdateOutcome(update_id='1')
    telem_man.store_update_outcome(mock_outcome)
    out = telem_man.list_events()
    print(out)

