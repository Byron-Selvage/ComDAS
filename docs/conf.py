import os
import sys

sys.path.insert(0, os.path.abspath(".."))

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "ComDAS"
copyright = "2026, Byron Selvage"
author = "Byron Selvage"
release = "0.1.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx_autodoc_typehints",
    "sphinx.ext.mathjax",
    "myst_nb",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "**.ipynb_checkpoints", "Thumbs.db", ".DS_Store"]

# -- API docs ----------------------------------------------------------------
autosummary_generate = True
autodoc_default_options = {
    "members": True,
    "show-inheritance": True,
    "ignore-module-all": True,
}
autodoc_member_order = "bysource"

# -- Example notebooks -------------------------------------------------------
# Notebooks are executed at build time; results are cached between builds.
nb_execution_mode = "cache"
nb_execution_timeout = 600
nb_execution_raise_on_error = True
myst_enable_extensions = ["dollarmath", "amsmath"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = []
html_title = "ComDAS"
html_baseurl = "https://byron-selvage.github.io/ComDAS/"
html_theme_options = {
    "source_repository": "https://github.com/Byron-Selvage/ComDAS/",
    "source_branch": "main",
    "source_directory": "docs/",
}
