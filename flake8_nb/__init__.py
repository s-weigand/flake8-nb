# -*- coding: utf-8 -*-

"""Top-level package for flake8-nb."""

__author__ = """Sebastian Weigand"""
__email__ = "s.weigand.phy@gmail.com"
__version__ = "0.1.0"

import flake8

FLAKE8_VERSION_TUPLE = tuple(map(int, flake8.__version__.split(".")))
