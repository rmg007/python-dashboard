import os
import sys
sys.path.insert(0, os.path.abspath('../..'))

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",  # for Google-style docstrings
]

autodoc_mock_imports = ["dash", "plotly", "pandas"]

project = 'Permit Dashboard'
author = 'Your Name or Team'
release = '1.0'
