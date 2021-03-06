# Configuration file for the Sphinx documentation builder.

# -- Project information

project = 'Paraqus'
copyright = '2022, Furlan & Stollberg'
author = 'Furlan, Stollberg'

# this should ideally integrate in some way...
release = '0.0'
version = '0.0.1'

# -- General configuration

import os
import sys
sys.path.insert(0, os.path.abspath('../../src/'))

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'sphinx.ext.napoleon',
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
}
intersphinx_disabled_domains = ['std']

templates_path = ['_templates']

autodoc_mock_imports = ["abaqus", "numpy"]

# -- Options for HTML output

html_theme = 'sphinx_rtd_theme'

# -- Options for EPUB output
epub_show_urls = 'footnote'
