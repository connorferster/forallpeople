# Changelog

## 3.4.1

### Fixed

- **Wrong display of a value with a factor that no unit has.** A unit with a factor (such as a tonne, `t`, with `Factor: 1/1000`) gives its factor to the quantities made from it. When no unit in the environment has that factor and those dimensions, the value is shown in SI units, but it was still scaled by the factor: `1 * t / m**3` displayed as `1.000 kg·m⁻³` instead of `1000.000 kg·m⁻³` ([handcalcs #352](https://github.com/connorferster/handcalcs/issues/352)). The value itself (`.value`) was always right.

## 3.4.0

**Unit values change:** several units in the bundled environments had wrong definitions and now have the correct size. Calculations that used them give different (correct) results. Five units are removed.

### Fixed

- **Wrong unit factors in the bundled environments.** The factor parser evaluates left to right with no operator precedence, so factors written with `**` were wrong; other factors were inverted.
  - `us_customary`: `psi`, `ksi`, `pci` and `kci` were wrong (`**` precedence); `ton` is now 2000 lbf (it was treated as a mass); `F` (Fahrenheit degree) was inverted.
  - `structural`: `pci`, `kci`, `lbft2` and `kft2` were wrong (`**` precedence).
  - `thermal`: `psi` and `ksi` were wrong (`**` precedence); `kg_h`, `g_mol` and `kg_kmol` were inverted; `bar` is now 100 000 Pa and displays as "bar".
- **Wrong unit symbols.** `mile` displayed as "yard"; `pci` and `kci` displayed as "pcf" and "kcf".
- **Wrong displays in `us_customary` and `thermal`.** In `us_customary`, `0.003785*si.m**3` displayed as `3.785 mm³`; it is now `3785000.000 mm³`. In `thermal`, `0.01*si.kg/si.s` displayed as `10.000 mkg·s⁻¹`; it is now `0.010 kg·s⁻¹`.

### Removed

- `acre`, `fl_ounce` and `quart` from `us_customary`, and `kg_s` and `kg_m3` from `thermal`. They caused the wrong displays above. (`fl_ounce` and `quart` also had wrong sizes: 1 fl oz was 33 814 m³.)

### Documentation

- New documentation site: https://forallpeople.structuralpython.com

## 3.3.0

### Changed

- **`parse` keeps the SI prefix a quantity was written with.** A quantity written in a single SI-prefixed unit now displays in that unit: `si.parse("0.6 kPa")` is `0.600 kPa` (was `600.000 Pa`) and `si.parse("4000 mm")` is `4000.000 mm` (was `4.000 m`). This applies to prefixed SI units (`kN·m`, `μm`, `mg`) and to environment units that are exactly a prefix on an SI unit (`kPa`, `mm`, `kN`, `MPa` in `structural`). Compound expressions (`kN/m^3`, `kN*m`) and units with a factor (`kip`, `ft`) are unchanged.
  - **`float()` of such a value is now in the authored unit.** `float(si.parse("0.6 kPa"))` is `0.6` (was `600.0`), and `float(si.parse("4000 mm"))` is `4000.0` (was `4.0`). This matches how `float()` already follows the displayed prefix. Use `.value` for SI, which is unchanged.
  - Serialization is unaffected: `to_dict` already stores `prefixed`, and `value` stays SI.
- **`parse_tree` (and the `yaml+units` loader) only parses quantity strings**: a number, alone or followed by whitespace and unit text. Strings like `"000.000.000"`, `"2026-014"`, `"2026-10-29"`, `"38x140"` and `"350MPa"` are now left as strings instead of raising `UnitParseError`. `si.parse("350MPa")` itself still works.
- **`Physical.to_dict()` records the active environment** in an `"environment"` field (omitted when none is loaded). It is informational: `from_dict`, `si.load(s)` and `json_object_hook` ignore it. The serialization format version is still `1`.
- **The YMPrint plugin decodes quantities in the environment they were written in.** If no environment is active, decoding loads the bundled environment recorded with the value. It never replaces an active environment; a mismatch, or an unbundled (custom) environment, is warned about once per process.

### Fixed

- **Raising a prefixed `Physical` to a power keeps its units.** `(4 * si.m).prefix("m") ** 2` returned the float `16000000.0`; it now returns `16000000.000 mm²`.
