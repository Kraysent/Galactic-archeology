from typing import List

import sphinx_rtd_theme

# -- Project information -----------------------------------------------------

project = "OMTool"
copyright = "2022, Artyom Zaporozhets"
author = "Artyom Zaporozhets"

release = "0.4.0"

# -- General configuration ---------------------------------------------------

extensions: List[str] = []

templates_path = ["_templates"]

exclude_patterns: List[str] = []

# -- Options for HTML output -------------------------------------------------

html_theme = 'sphinx_rtd_theme'
htm_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

html_static_path = ["_static"]
