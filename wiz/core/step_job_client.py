import json
from json import JSONDecodeError
from typing import Dict, Optional

from k8_kat.res.job.kat_job import KatJob
from k8_kat.res.pod.kat_pod import KatPod
from wiz.core import step_job_prep
from wiz.core.types import JobStatus, JobStatusPart
from wiz.core.wiz_app import wiz_app


def _fmt_status_part(raw: Dict, index: int) -> JobStatusPart:
  """
  Parses job status dump to extract name, status and percentage.
  :param raw: raw status dump, in dict form.
  :param index: passed job index to record job part.
  :return: instance of JobsStatusPart typedict.
  """
  return JobStatusPart(
    name=raw.get('name', f'Job Part {index + 1}'),
    status=raw.get('status', 'Working'),
    pct = int(raw.get('pct')) if raw.get('pct') else None
  )


def _fmt_raw_status(raw_dump: Dict, logs) -> JobStatus:
  """
  Parses the extracted pod status(es) and packages together with logs into an
  output.
  :param raw_dump: raw status dump to be analyzed for status.
  :param logs: logs to be passed to output.
  :return: instance of JobStatus typedict with extracted status parts and logs.
  """
  raw_parts = raw_dump if type(raw_dump) == list else [raw_dump]
  parts = [_fmt_status_part(raw, i) for i, raw in enumerate(raw_parts)]
  return JobStatus(
    parts=parts,
    logs=logs
  )


def find_job(job_id: str) -> KatJob:
  """
  Finds the instance of the job by job id.
  :param job_id: job id to locate the job pod.
  :return: job pod (KatJob) instance.
  """
  return KatJob.find(job_id, wiz_app.ns)


def find_worker_pod(job_id) -> Optional[KatPod]:
  """
  Finds the right worked pod by job id.
  :param job_id: job id to locate the worker pod.
  :return: worker pod (KatPod) instance.
  """
  return next(iter(find_job(job_id).pods()), None)


def cleanup(job_id: str):
  """
  Finds the instance of a job by job id, then deletes it. Does not wait for
  delete to finish.
  :param job_id: job id to locate the job pod.
  """
  job =  find_job(job_id)
  job.delete(wait_until_gone=False)


def extract_status(pod: KatPod):
  """
  Extracts pod status and deserializes from JSON to Python dict.
  :param pod: pod (KatPod object) whose status to extract.
  :return: deserialized pod status or {} if none found.
  """
  status_str = pod.shell_exec(f"cat {step_job_prep.status_fname}")
  status_str = status_str.replace("\'", "\"") if status_str else None
  try:
    return json.loads((status_str or {}))
  except JSONDecodeError:
    return {}


def compute_job_status(job_id: str) -> Optional[JobStatus]:
  """
  Computes job status. Example output:
    JobStatus(
      parts=[
        JobStatusPart(
          name=raw.get('name', f'Job Part {index + 1}'),
          status=raw.get('status', 'Working'),
          pct = int(raw.get('pct')) if raw.get('pct') else None
        )
      ],
      logs=logs
    )
  :param job_id: id to locate the job.
  :return: instance of JobStatus as above.
  """
  pod = find_worker_pod(job_id)
  if pod:
    logs = pod.log_lines() if pod else []
    return _fmt_raw_status(extract_status(pod), logs)
  else:
    return None
