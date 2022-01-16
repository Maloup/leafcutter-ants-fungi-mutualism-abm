#!/usr/bin/env python
from setuptools import setup, find_packages

requires = ["mesa"]

setup(
    name="leafcutter_ants_fungi_mutualism",
    version="0.0.1",
    packages=find_packages(),
    install_requires=requires,
)
