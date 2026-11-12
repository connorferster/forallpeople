"""Sphinx configuration for the forallpeople documentation."""

import json
import pathlib

import forallpeople

DOCS_DIR = pathlib.Path(__file__).parent
ENVIRONMENTS_DIR = pathlib.Path(forallpeople.__file__).parent / "environments"

# -- Project information -----------------------------------------------------

project = "forallpeople"
author = "Connor Ferster"
copyright = "2019-%Y, Connor Ferster"
release = forallpeople.__version__
version = ".".join(release.split(".")[:2])

# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
    "sphinx_design",
    "myst_nb",
]

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "myst-nb",
}

exclude_patterns = ["_build", "_generated", "Thumbs.db", ".DS_Store"]

myst_enable_extensions = ["colon_fence", "deflist", "fieldlist", "dollarmath"]
myst_heading_anchors = 3

# The guide pages are MyST notebooks: their code cells run on every build, so
# the outputs shown are always those of the installed forallpeople, and an
# example that stops working fails the build.
nb_execution_mode = "force"
nb_execution_raise_on_error = True
nb_execution_timeout = 60
nb_merge_streams = True

autodoc_default_options = {
    "members": True,
    "show-inheritance": False,
    "member-order": "bysource",
}
autodoc_typehints = "description"
autoclass_content = "class"

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

# -- HTML output -------------------------------------------------------------

html_theme = "shibuya"
html_title = "forallpeople"
html_baseurl = "https://forallpeople.structuralpython.com/"
html_copy_source = False
html_static_path = ["_static"]
html_css_files = ["custom.css"]

html_theme_options = {
    "github_url": "https://github.com/connorferster/forallpeople",
    "accent_color": "teal",
    "nav_links": [
        {"title": "Guide", "url": "getting-started"},
        {"title": "Environments", "url": "guide/environments"},
        {"title": "API", "url": "api/index"},
    ],
}

html_context = {
    "source_type": "github",
    "source_user": "connorferster",
    "source_repo": "forallpeople",
    "source_version": "main",
    "source_docs_path": "/docs/",
}

# -- Bundled environment tables ----------------------------------------------
# The reference tables of the bundled environments are generated from their
# JSON files on every build (into docs/_generated/, git-ignored), so they
# always match the package. Each definition is shown as it is written in the
# file.

BUNDLED_ENVIRONMENTS = [
    ("default", "The SI derived units, and minutes, hours and days."),
    (
        "structural",
        "SI and US customary units used in structural engineering: forces, "
        "moments, line loads, pressures and densities.",
    ),
    (
        "us_structural",
        "US customary units for structural engineering: lb and kip with in and "
        "ft, in every combination of force times or over length to the fourth "
        "power. Mixed-unit results are shown in the `Default` units (in, kip, "
        "kip·ft, kip/ft, ksi, pcf, ...).",
    ),
    ("us_customary", "Common US customary units of length, area, volume, force and mass."),
    ("electrical", "Units for electrical engineering."),
    ("thermal", "Units for building envelope and heat transfer calculations."),
]

BASE_UNITS = ("kg", "m", "s", "A", "cd", "K", "mol")
SUPERSCRIPTS = str.maketrans("-0123456789.", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹·")


def _dimension_text(dimension: list) -> str:
    parts = []
    for unit, power in zip(BASE_UNITS, dimension):
        if power == 0:
            continue
        parts.append(unit if power == 1 else unit + str(power).translate(SUPERSCRIPTS))
    return "·".join(parts) or "1"


def _definition_text(definition: dict) -> str:
    if "Factor" in definition:
        return f"Factor `{definition['Factor']}`"
    if "Value" in definition:
        return f"Value `{definition['Value']}`"
    return "SI unit"


def _write_environment_tables(app):
    out_dir = DOCS_DIR / "_generated"
    out_dir.mkdir(exist_ok=True)
    for name, description in BUNDLED_ENVIRONMENTS:
        definitions = json.loads(
            (ENVIRONMENTS_DIR / f"{name}.json").read_text(encoding="utf-8")
        )
        lines = [
            description,
            "",
            "| Variable | Displays as | Dimensions | Definition |",
            "|---|---|---|---|",
        ]
        for unit, definition in definitions.items():
            symbol = definition.get("Symbol") or unit
            lines.append(
                f"| `{unit}` | {symbol} | {_dimension_text(definition['Dimension'])} "
                f"| {_definition_text(definition)} |"
            )
        (out_dir / f"environment-{name}.md").write_text(
            "\n".join(lines) + "\n", encoding="utf-8"
        )


def setup(app):
    app.connect("builder-inited", _write_environment_tables)
