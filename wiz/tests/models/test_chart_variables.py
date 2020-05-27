from typing import Type

from wiz.model.base.wiz_model import WizModel
from wiz.model.chart_variable.chart_variable import ChartVariable
from wiz.tests.models.test_wiz_model import Base


class TestChartVariables(Base.TestWizModel):

  @classmethod
  def model_class(cls) -> Type[WizModel]:
    return ChartVariable
