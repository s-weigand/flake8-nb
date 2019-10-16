# -*- coding: utf-8 -*-

"""Top-level package for flake8-nb."""

__author__ = """Sebastian Weigand"""
__email__ = "s.weigand.phy@gmail.com"
__version__ = "0.1.0"

import os

import flake8

from .flake8_integration.formatter import IpynbFormatter  # noqa: F401

__all__ = "IpynbFormatter"

FLAKE8_VERSION_TUPLE = tuple(map(int, flake8.__version__.split(".")))

tox_env_name = os.environ.get("TOX_ENV_NAME", None)
if tox_env_name and tox_env_name == "flake8-nightly":
    FLAKE8_VERSION_TUPLE = (3, 8, 0)
