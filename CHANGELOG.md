# Changelog

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
