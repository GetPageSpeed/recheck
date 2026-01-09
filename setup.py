#!/usr/bin/env python
"""Setup script for backwards compatibility with Python 3.6 pip."""

from setuptools import setup

# All configuration is in pyproject.toml
# This file exists for compatibility with older pip versions
# that don't support PEP 660 (editable installs from pyproject.toml)
setup()
