from k8_kat.res.base.kat_res import KatRes


def basic(res: KatRes):
  return dict(
    kind=res.kind,
    name=res.name,
    status=res.ternary_status()
  )
