import json
from json import JSONDecodeError
from typing import Dict, Optional

from k8_kat.res.job.kat_job import KatJob
from k8_kat.res.pod.kat_pod import KatPod
from wiz.core import step_job_prep
from wiz.core.types import JobStatus, JobStatusPart
from wiz.core.wiz_globals import wiz_app


def _fmt_status_part(raw: Dict, index: int) -> JobStatusPart:
  return JobStatusPart(
    name=raw.get('name', f'Job Part {index + 1}'),
    status=raw.get('status', 'Working'),
    pct = int(raw.get('pct')) if raw.get('pct') else None
  )


def _fmt_raw_status(raw_dump: Dict, logs) -> JobStatus:
  raw_parts = raw_dump if type(raw_dump) == list else [raw_dump]
  parts = [_fmt_status_part(raw, i) for i, raw in enumerate(raw_parts)]
  return JobStatus(
    parts=parts,
    logs=logs
  )


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


def compute_job_status(job_id: str) -> Optional[JobStatus]:
  pod = find_worker_pod(job_id)
  if pod:
    pod = find_worker_pod(job_id)
    logs = pod.log_lines() if pod else []
    return _fmt_raw_status(extract_status(pod), logs)
  else:
    return None
