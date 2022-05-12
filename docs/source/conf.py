import sphinx_pdj_theme

# -- Project information -----------------------------------------------------

project = "OMTool"
copyright = "2022, Kraysent"
author = "Kraysent"

# The full version, including alpha/beta/rc tags
release = "0.1.0"

# -- General configuration ---------------------------------------------------

extensions: list[str] = []

templates_path = ["_templates"]

exclude_patterns: list[str] = []

# -- Options for HTML output -------------------------------------------------

html_theme = "sphinx_pdj_theme"
htm_theme_path = [sphinx_pdj_theme.get_html_theme_path()]
html_theme_options = {"style": "darker"}

html_static_path = ["_static"]
