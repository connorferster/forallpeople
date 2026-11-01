# Writing your own environment

An environment is a JSON file. Each entry defines one unit, keyed by its
variable name:

```json
{
    "mm": {
        "Dimension": [0, 1, 0, 0, 0, 0, 0],
        "Value": 0.001
    },
    "ft": {
        "Dimension": [0, 1, 0, 0, 0, 0, 0],
        "Factor": "1/0.3048",
        "Symbol": "ft"
    },
    "kN": {
        "Dimension": [1, 1, -2, 0, 0, 0, 0],
        "Value": 1000
    },
    "psf": {
        "Dimension": [1, -1, -2, 0, 0, 0, 0],
        "Factor": "0.3048**2/0.45359237/9.80665",
        "Symbol": "psf"
    }
}
```

Load it by path:

```python
import forallpeople as si
si.environment("path/to/my_units.json")
```

The simplest way to start is to copy a bundled environment and edit it. The
bundled files are in the `environments` folder of the installed package
(`pathlib.Path(si.__file__).parent / "environments"`), and are listed in
{doc}`environments`.

## The keys of a definition

`Dimension` (required)
: The powers of the seven SI base units, **in the order**
  `[kg, m, s, A, cd, K, mol]`. A newton (kg·m·s⁻²) is `[1, 1, -2, 0, 0, 0, 0]`.

`Value` (optional, default `1`)
: For an SI unit: the size of one of this unit in SI base units. A kilonewton
  is `1000`. Units with a `Value` are SI units, so quantities in them are still
  prefixed automatically: `kN` is a convenient variable, and `1000 N` displays
  as `1.000 kN` either way.

`Factor` (optional, default `1`)
: For a non-SI unit: the number that a value in SI base units is
  **multiplied by** to give the value in this unit. A foot is `"1/0.3048"`,
  because 1 m is 1/0.3048 ft. A unit with a factor is a **defined** unit. It is
  never prefixed.

`Symbol` (optional)
: How the unit is displayed. Without it, the variable name is used. Give every
  defined unit a symbol.

`Default` (optional, default `false`)
: Marks a defined unit as the fallback for its dimensions (see below).

The variable name must be a valid Python identifier, because the unit is
loaded as a variable (`si.psf`). Use the symbol for the display form:
`"lb_ft"` can display as `"lb/ft"`.

## Factor expressions

A factor can be a number, or a string with an arithmetic expression of
numbers, `+`, `-`, `*`, `/` and `**`. Strings let you write a factor from the
exact legal definitions of its parts, e.g. 1 lb = 0.45359237 kg and
1 ft = 0.3048 m:

```json
"Factor": "0.3048**2/0.45359237/9.80665"
```

The expression is calculated with exact fractions, not `eval()`. Only the
numbers and operators in the string are read: a string that starts with a
letter is rejected, but letters later in the string are ignored, so check
factors carefully.

```{important}
The expression is evaluated **strictly from left to right**: there is no
operator precedence, and no parentheses. `2+3*4` gives `20`, not `14`. In
particular, `**` applies to everything before it, so `0.3048**2/12**2` means
`((0.3048**2)/12)**2`. Write `0.3048**2/144`, or `0.0254**2`, instead. Check a
new factor with:

    from forallpeople.environment import evaluate_factor_expression
    float(evaluate_factor_expression("0.3048**2/144"))
```

## Default units

A calculation in defined units can produce a factor that no unit in the
environment has, e.g. `lb × m / ft`, which mixes unit systems. Without a
default, the result falls back to an SI unit, which is surprising in the
middle of a calculation in US units.

Mark one defined unit of each dimension as `"Default": true` to use it in that
case. With this definition, `5 * lb * m / ft` displays as `16.404 lb`:

```json
"lb": {
    "Dimension": [1, 1, -2, 0, 0, 0, 0],
    "Factor": "1/0.45359237/9.80665",
    "Symbol": "lb",
    "Default": true
}
```

A default only applies to quantities that have a factor. Quantities in SI
units are never displayed in a default unit.

## Tips

- One unit per meaning: if two units have the same dimensions (`J` and `N·m`),
  define the one your calculations mean, or define both and convert with
  `.to()`. See {doc}`../background`.
- JSON has no comments and no trailing commas. Moving an entry from the middle
  of a file to the end is a common way to leave one behind.
- Key names are in title case (`"Dimension"`, not `"dimension"`).
- Only one environment is active per Python process. Loading another replaces
  it, including for modules that imported forallpeople separately.
