from datetime import datetime
from typing import Dict
from pathlib import Path

from flask import json

from k8_kat.utils.main.utils import deep_merge
from wiz.core import utils
from wiz.model.operations.operation import Operation

BASE_DIR = '/tmp/nectar-wiz'


class JobOutcomeRecord:
  pass


class StepRecord:

  def __init__(self, raw_record: Dict):
    self.step_id = raw_record['step_id']
    self.stage_id = raw_record['stage_id']
    self.started_at = None
    self.finished_at = None
    self.assignments = raw_record.get('assignments', {})
    self.computed = raw_record.get('computed', {})
    self.job_outcome = raw_record.get('job_outcome', {})

  def serialize(self):
    return dict(
      step_id=self.step_id,
      stage_id=self.step_id,
    )


class OperationRecord:

  def __init__(self, raw_record: Dict):
    self.hard_id = raw_record.get('id')
    self.step_records = [StepRecord(raw) for raw in raw_record.get('steps', [])]

  def record_step_started(self, step):
    self.step_records.append(StepRecord(dict(
      step_id=step.key,
      stage_key=step.parent.key,
      started_at=str(datetime.now())
    )))

  def record_step_finished(self, step):
    pass

  def record_step_terminated(self, step_name: str, bundle):
    pass

  def find_step_record(self, step):
    predicate = lambda sr: sr.step_id == step.key and \
                           sr.stage_id == step.parent.key
    return next((sr for sr in self.step_records if predicate(sr)), None)

  def assignments(self):
    merged = {}
    for step_record in self.step_records:
      merged = deep_merge(merged, step_record.assignments)
    return merged


class OperationStateRecorder:
  def __init__(self, ser_operation_record: Dict):
    self.operation_record = OperationRecord(ser_operation_record)

  def record_step_started(self, step):
    self.operation_record.record_step_started(step)

  def record_step_terminated(self):
    pass

  def assignments(self) -> Dict:
    return self.operation_record.assignments()

  @classmethod
  def retrieve_for_writing(cls, _id):
    raw = read_serialized_operation_state(_id, coerce=True)
    return OperationStateRecorder(raw)


sample_record = {
  'id': 'random-str',
  'operation_id': 'installation',
  'steps': [
    {
      'id': 'strategy',
      'stage_id': 'asd',
      'started_at': 'datetime',
      'finished_at': 'datetime',
      'assignments': {
        'hub.storage.strategy': 'internal'
      },
      'computed': {
        'hub.storage.strategy': 'internal'
      },
      'job': {
        'id': 'random-str',
        'started_at': 'datetime',
        'finished_at': 'datetime',
        'exit_code': '0',
        'logs': []
      }
    }
  ]
}


def write_serialized_operation_state(_id, serialization: Dict):
  file = Path(f'{BASE_DIR}/osr-{_id}.json')

  with file.open('w+') as writeable_file:
    writeable_file.write(json.dumps(serialization))


def read_serialized_operation_state(record_id, coerce=True) -> Dict:
  file = Path(f'{BASE_DIR}/osr-{record_id}.json')

  if not file.exists() and coerce:
    file.touch(exist_ok=True)

  if file.exists() or coerce:
    with file.open('r') as readable_file:
      contents = readable_file.read()
      return json.loads(contents)
  else:
    return None


def commit_op_started(operation: Operation):
  pass
