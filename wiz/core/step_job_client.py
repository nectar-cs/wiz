import json
from json import JSONDecodeError
from typing import Dict, Union, List, Optional

from k8_kat.res.job.kat_job import KatJob
from k8_kat.res.pod.kat_pod import KatPod
from wiz.core import step_job_prep
from wiz.core.wiz_globals import wiz_app


class JobStatusPart:
  def __init__(self, raw: Dict[str, str], index: int):
    self.name = raw.get('name', f'Job Part {index + 1}')
    self.status = raw.get('status', 'Working')
    self.pct = int(raw.get('pct')) if raw.get('pct') else None


class JobStatus:
  def __init__(self, raw_dump: Union[Dict, List[Dict]], logs):
    raw_parts = raw_dump if type(raw_dump) == list else [raw_dump]
    self.parts = [JobStatusPart(part, i) for (i, part) in enumerate(raw_parts)]
    self.logs = logs


def find_job(job_id: str) -> KatJob:
  return KatJob.find(job_id, wiz_app.ns)


def find_worker_pod(job_id) -> Optional[KatPod]:
  return next(iter(find_job(job_id).pods()), None)


def cleanup(job_id: str):
  job =  find_job(job_id)
  job.delete(wait_until_gone=False)


def extract_status(pod: KatPod):
  status_str = pod.shell_exec(f"cat {step_job_prep.status_fname}")
  status_str = status_str.replace("\'", "\"") if status_str else None
  try:
    return json.loads((status_str or {}))
  except JSONDecodeError:
    return {}


def job_status_bundle(job_id: str) -> Optional[JobStatus]:
  pod = find_worker_pod(job_id)
  if pod:
    pod = find_worker_pod(job_id)
    logs = pod.log_lines() if pod else []
    return JobStatus(extract_status(pod), logs)
  else:
    return None


def read_job_ternary_status(job_id: str):
  main_pod: KatPod = find_worker_pod(job_id)
  if main_pod:
    if main_pod.has_succeeded():
      return 'positive'
    elif main_pod.is_running_normally():
      return 'pending'
    else:
      return 'negative'
  else:
    return 'pending'
