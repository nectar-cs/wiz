from datetime import datetime
from typing import Dict, List

from nectwiz.core.core import prom_api_client
from nectwiz.model.supply.prometheus_supplier import PrometheusSupplier


class PrometheusTimeSeriesSupplier(PrometheusSupplier):

  def _compute(self):
    result = self.fetch_value()
    if result:
      aggregated = agg_series(result)
      print("AGGREGATED FINAL")
      print(aggregated)
      return aggregated
    else:
      return None

  def fetch_value(self):
    response = prom_api_client.compute_series(
      self.query_expr,
      self.step,
      self.t0,
      self.tn
    )
    return self.extract_datapoints(response)


def infer_series_key(metric: Dict) -> str:
  as_items = list(metric.items())
  if len(as_items) == 1:
    return as_items[0][1]
  elif len(as_items) == 0:
    return 'value'
  else:
    print(f"[nectwiz:prom_series_computer] can't handle n-dim metric {metric}")
    return 'value'


def subserie_for_metric(subseries: List, metric_key: str) -> List:
  if metric_key == 'value':
    if len(subseries) == 1:
      return subseries[0]
    else:
      print("DANGER key is 'value' but +1 metric types!")
      return []

  for sub_series in subseries:
    if len(sub_series['metric']) > 0:
      if sub_series['metric'].values()[0] == metric_key:
        return sub_series
    elif len(sub_series['metric']) == 0:
      return sub_series

  print(f"DANGER no subseries for {metric_key}")
  return []


def warn_agg_series(query_result: List[Dict]):
  metric_key_sets = [set(g['metric'].keys()) for g in query_result]
  if len(metric_key_sets) >= 2:
    for i in range(len(metric_key_sets)):
      pass


def find_or_create_entry(output: List, epoch: int) -> Dict:
  for datapoint in output:
    if datapoint['epoch'] == epoch:
      return datapoint

  datapoint = {'epoch': epoch}
  output.append(datapoint)
  return datapoint


def agg_series(query_result: List[Dict]) -> List:
  output = []
  warn_agg_series(query_result)
  for grouping in query_result:
    key = infer_series_key(grouping.get('metric'))
    for datapoint in grouping.get('values'):
      if len(datapoint) == 2:
        epoch, computed_val = datapoint
        entry = find_or_create_entry(output, epoch)
        entry[key] = float(computed_val)
      else:
        print(f"[nectwiz:prom_series_computer] !=2 entry val {datapoint}")

  for datapoint in output:
    epoch = datapoint['epoch']
    del datapoint['epoch']
    datapoint['timestamp'] = str(datetime.fromtimestamp(epoch))

  return output
