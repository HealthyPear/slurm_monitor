"""Sphinx configuration for SLURM Monitoring documentation"""

import os
import sys

# Add src directory to path for autodoc
sys.path.insert(0, os.path.abspath("../src"))

# Project information
project = "SLURM Monitoring"
copyright = "2026, SLURM Monitoring Contributors"
author = "SLURM Admin"
release = "0.1.0"

# Extensions
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx_rtd_theme",
]

# Autodoc settings
autosummary_generate = True
autodoc_typehints = "description"
autodoc_member_order = "bysource"

# Theme settings
html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "analytics_id": "",
    "canonical_url": "",
    "collapse_navigation": True,
    "display_version": True,
    "logo_only": False,
    "prev_next_buttons_location": "bottom",
    "style_external_links": False,
    "style_nav_header_background": "#2c3e50",
    "vcs_pageview_mode": "",
}

html_static_path = ["_static"]
html_logo = None
html_favicon = None

# Documentation setup
master_doc = "index"
source_suffix = ".rst"
language = "en"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
pygments_style = "sphinx"
html_use_index = True
