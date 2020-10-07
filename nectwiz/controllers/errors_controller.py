from flask import Blueprint, jsonify

from nectwiz.core.core import job_client
from nectwiz.model.error.error_diagnosis import ErrorDiagnosis
from nectwiz.model.error.error_handler import find_handler, compute_diagnoses_ids, async_compute_diagnoses_ids
from nectwiz.model.error.errors_man import errors_man
from nectwiz.serializers import err_serializer

controller = Blueprint('errors_controller', __name__)

BASE_PATH = '/api/errors'

@controller.route(f'{BASE_PATH}/<error_id>/diagnose', methods=['POST'])
def start_diagnose_search(error_id: str):
  errdict = errors_man.find_error(error_id)
  if errdict:
    handler = find_handler(errdict)
    if handler:
      job_id = job_client.enqueue_func(async_compute_diagnoses_ids, handler.id())
      return jsonify(status='running', job_id=job_id)
    else:
      return jsonify(status='not-found')
  else:
    return jsonify(status='not-found')


@controller.route(f'{BASE_PATH}/<job_id>/diagnoses')
def diagnose_status(job_id: str):
  job = job_client.find_job(job_id)
  if job.is_finished:
    diagnoses_ids = job.meta['result']
    print(f"BTW result was {job.result} vs {diagnoses_ids}")
    diagnoses = list(map(ErrorDiagnosis.inflate, diagnoses_ids))
    serializer = lambda d: err_serializer.ser_err_diagnosis(d)
    serialized = list(map(serializer, diagnoses))
    return jsonify(status='ready', diagnosis=serialized)
  elif job.is_failed:
    return jsonify(status='error')
  else:
    return jsonify(status='pending')
