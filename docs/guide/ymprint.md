# Quantities in YMPrint projects

With [YMPrint](https://github.com/StructuralPython/ymprint) 0.8.1 or later
installed, forallpeople registers itself as a YMPrint plugin. There is nothing
to configure.

## Exported values stay quantities

A quantity that a document exports (`_export`) or a script publishes is
written in forallpeople's exact {doc}`JSON form <json>`. Whoever reads it back
through `_data` gets a `Physical`, not a dict.

When a quantity is read back and no environment is active yet, the bundled
environment it was written in is loaded, so that it displays as it was written
(`16.099 kN/m`, not `16099.200 kg·s⁻²`). An active environment is never
replaced. If the quantity was written in a different environment, or in a
custom environment that isn't bundled, forallpeople warns once.

## Data files with units

The `yaml+units` loader reads YAML files written with units:

```yaml
# project.ymprint.yml
_data:
  geometry: {path: geometry.yml, loader: yaml+units}
```

```yaml
# geometry.yml
_environment: structural
B01: {span: 6 m, w_DL: 2.5 kN/m, f_y: 350 MPa}
```

Every quantity string is parsed as by {func}`~forallpeople.parse_tree` (see
{doc}`parsing`). Strings like `2026-014` or `000.000.000` are left alone.

The file names its environment in `_environment`: either the name of a bundled
environment, or the path to an environment `.json` file, relative to the data
file. There is no default environment.

```{note}
forallpeople has one active environment per Python process. A data file that
names a different environment from the active one replaces it, with a
warning.
```
