from nectwiz.model.base.wiz_model import WizModel


class SystemCheck(WizModel):

  def predicate(self):
    pass

  # all deps have > 0 green pods
  # traffic between two arbitrary points work
  # can curl publicly
  # no pods have suspicious restart rates


