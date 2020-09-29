from typing import Dict, List, Optional

from typing_extensions import TypedDict

from nectwiz.model.base.wiz_model import WizModel

class ErrorContext(TypedDict):
  data: Dict


class ErrorFix(TypedDict):
  goto: str


class Diagnosis(TypedDict):
  text: str
  md_src: Optional[str]
  fixes: List[ErrorFix]

# concept: Relevance Hierarchy

class ErrorHandler(WizModel):
  def compute_diagnosis(self, err_ctx: ErrorContext) -> Diagnosis:
    problem_pod = KatPod.find()
    if pod.died_low_memory():
      say_this
    elif pod.permissions:
      pass
    else:
      pass


class SomeHandler(ErrorHandler):
  pass


errors_man = dict(
  unsolved_errors=[]
)
