---
file_format: mystnb
kernelspec:
  name: python3
  display_name: Python 3
---

# Saving quantities to JSON

```{code-cell} ipython3
import forallpeople as si
si.environment("structural")
```

{meth}`~forallpeople.Physical.to_dict` returns a JSON-compatible dict that
describes a quantity exactly, and {meth}`~forallpeople.Physical.from_dict`
reads it back:

```{code-cell} ipython3
q = 30.2 * si.kN
q.to_dict()
```

`si.dumps` and `si.loads` (and `si.dump` and `si.load`, for files) work like
their `json` equivalents, and encode and decode the quantities anywhere in the
data:

```{code-cell} ipython3
text = si.dumps({"Vr": 30.2 * si.kN, "phi": 0.9, "L": 12 * si.ft})
si.loads(text)
```

- **The round trip is exact.** `value` is always in SI units, and a
  fractional factor (e.g. for `ft`) is stored exactly, as `"n/d"`.
- **Loading needs no environment.** `environment` (the environment that was
  active, left out if there was none) and `display` are for people reading the
  JSON. `si.loads` ignores them and never loads an environment.

To use the standard library's `json` module directly, pass forallpeople's
hooks:

```python
import json

text = json.dumps(data, default=si.json_default)
data = json.loads(text, object_hook=si.json_object_hook)
```

`json_default` raises `TypeError` for anything that isn't a `Physical`, as
`json` expects, so it can be combined with other encoders.
