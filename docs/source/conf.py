# Configuration file for the Sphinx documentation builder.
import os
import sys
import sphinx_rtd_theme

sys.path.insert(0, os.path.abspath('../..'))

project = 'classconfig'
copyright = '2023, Martin Dočekal'
author = 'Martin Dočekal'
release = '1.0.13'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx_rtd_theme',
]

templates_path = ['_templates']
exclude_patterns = []

html_theme = 'sphinx_rtd_theme'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_static_path = ['_static']

html_theme_options = {
    'navigation_depth': 4,
    'collapse_navigation': False,
    'sticky_navigation': True,
}
