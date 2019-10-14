# -*- coding: utf-8 -*-

"""Top-level package for flake8-nb."""

__author__ = """Sebastian Weigand"""
__email__ = "s.weigand.phy@gmail.com"
__version__ = "0.1.0"

import flake8

from .flake8_integration.formatter import IpynbFormatter  # noqa: F401

__all__ = "IpynbFormatter"

FLAKE8_VERSION_TUPLE = tuple(map(int, flake8.__version__.split(".")))
