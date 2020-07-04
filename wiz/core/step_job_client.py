from typing import Dict, Union, List

from k8_kat.res.config_map.kat_map import KatMap


class JobStatusPart:
  def __init__(self, raw: Dict[str, str], index: int):
    self.name = raw.get('name', f'Job Part {index + 1}')
    self.status = raw.get('status', 'Working')
    self.pct = int(raw.get('pct')) if raw.get('pct') else None


class JobStatus:

  def __init__(self, raw_dump: Union[Dict, List[Dict]]):
    raw_parts = raw_dump if type(raw_dump) == list else [raw_dump]
    self.parts = [JobStatusPart(part, i) for (i, part) in enumerate(raw_parts)]




def load_config_map() -> KatMap:
  pass


def list_jobs_entries():
  pass


def find_job_entry(job_id: str):
  pass
