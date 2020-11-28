import traceback

from nectwiz.model.base.wiz_model import WizModel


class MetricsComputer(WizModel):

  def compute(self):
    # noinspection PyBroadException
    try:
      return self._do_compute()
    except:
      print(traceback.format_exc())
      print(f"[metrics_computer:compute] runtime err ^")

  def is_connected(self) -> bool:
    pass

  def _do_compute(self):
    raise NotImplementedError
