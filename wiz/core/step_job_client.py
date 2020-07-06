from typing import Dict, Union, List, Optional

from k8_kat.res.pod.kat_pod import KatPod

from k8_kat.res.config_map.kat_map import KatMap
from k8_kat.res.job.kat_job import KatJob
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


def find_job_cmap(job_id: str) -> KatMap:
  return KatMap.find(job_id, wiz_app.ns)


def find_job(job_id: str) -> KatJob:
  return KatJob.find(job_id, wiz_app.ns)


def find_worker_pod(job_id) -> Optional[KatPod]:
  job = find_job(job_id)
  return next(job.pods(), None)


def read_job_meta_status(job_id: str) -> Optional[JobStatus]:
  shared_config_map = find_job_cmap(job_id)
  if shared_config_map and shared_config_map.touch():
    raw_status = shared_config_map.jget(step_job_prep.status_fname)
    pod = find_worker_pod(job_id)
    logs = pod.raw_logs() if pod else []
    return JobStatus(raw_status, logs)
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
