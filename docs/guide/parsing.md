---
file_format: mystnb
kernelspec:
  name: python3
  display_name: Python 3
---

# Parsing quantities from text

Quantities can be read from strings, so that data files (YAML, JSON, CSV, ...)
can be written with their units next to the numbers.

```{code-cell} ipython3
import forallpeople as si
si.environment("structural")

si.parse("350 MPa"), si.parse("4.5 kN/m"), si.parse("5 kip·ft")
```

{func}`~forallpeople.parse` uses the units of the active environment. A string
with no units gives a float:

```{code-cell} ipython3
si.parse("0.9")
```

## Writing units

Units can be:

- units of the environment, by variable name (`kN`) or by symbol (`kip·ft`,
  `N/m`),
- SI base units (`kg`, `m`, `s`, ...), and
- SI-prefixed SI units, whether or not the environment defines them (`kN·m`,
  `μm`, `mg`).

Combine units with `*` or `·`, `/`, parentheses, and exponents written as
`**`, `^` or superscripts:

```{code-cell} ipython3
si.parse("164e6 mm**4"), si.parse("164e6 mm^4"), si.parse("164e6 mm⁴")
```

`/` is left-associative, as in Python: `kN/m/s` is `(kN/m)/s`. Use
parentheses for anything more than one `/`. Units separated only by a space,
such as `"30 kN m"`, are rejected as ambiguous.

The units are read with a small parser: `parse()` never calls `eval()`.

## Prefixes are kept

A quantity written in a single prefixed unit keeps that prefix, rather than
being given an automatic one:

```{code-cell} ipython3
q = si.parse("4000 mm")
q, float(q), q.value
```

So `float()` of a parsed quantity is the number that was written. Compound
units (`kN/m^3`) are prefixed automatically as usual.

## Checking the dimensions

Pass `expect` (a unit string or a `Physical`) to check that a value has the
dimensions you expect:

```{code-cell} ipython3
:tags: [raises-exception]
si.parse("350 kN", expect="MPa")
```

## Errors

A string that cannot be parsed raises {class}`~forallpeople.UnitParseError`,
a `ValueError`, with suggestions:

```{code-cell} ipython3
:tags: [raises-exception]
si.parse("30 kNm")
```

## Parsing nested data

{func}`~forallpeople.parse_tree` walks nested dicts, lists and tuples (for
example, the result of `yaml.safe_load` or `json.load`) and parses every
**quantity string**: a number on its own (`"12"`), or a number followed by a
space and units (`"350 MPa"`).

```{code-cell} ipython3
data = {
    "B01": {"span": "6 m", "w_DL": "2.5 kN/m", "f_y": "350 MPa"},
    "section": "W310x74",
    "issued": "2026-10-29",
    "storeys": "3",
}
si.parse_tree(data)
```

Keys, and strings with something attached directly to the number (such as
`"W310x74"`, `"2026-10-29"`, `"38x140"` and `"350MPa"`), are left alone. Write
a space between a number and its units. (`si.parse("350MPa")` does accept it.)

A quantity string that does not parse raises an error that names where it is:

```{code-cell} ipython3
:tags: [raises-exception]
si.parse_tree({"geometry": {"levels": "2 storeys"}})
```

With `strict=False`, it is left as a string instead.

To read a YAML file with units in a YMPrint project, see {doc}`ymprint`.
