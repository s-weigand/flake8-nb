# -*- coding: utf-8 -*-

"""Top-level package for flake8-nb."""

__author__ = """Sebastian Weigand"""
__email__ = "s.weigand.phy@gmail.com"
__version__ = "0.1.4"

import os

import flake8

from .flake8_integration.formatter import IpynbFormatter  # noqa: F401

__all__ = "IpynbFormatter"


def save_cast_int(int_str: str) -> int:
    """
    Helper function so the version number of prereleases (i.e. 3.8.0rc1)
    does not throw exceptions

    Parameters
    ----------
    int_str : str
        String which should represent a number.

    Returns
    -------
    int
        Int representation of int_str
    """
    try:
        return int(int_str)
    except ValueError:
        return 0


FLAKE8_VERSION_TUPLE = tuple(map(save_cast_int, flake8.__version__.split(".")))

# this is yet another hack, since the flake8 master still has
# the same version string as the latest PyPi release
tox_env_name = os.environ.get("TOX_ENV_NAME", None)
if tox_env_name and tox_env_name == "flake8-nightly":
    FLAKE8_VERSION_TUPLE = (3, 8, 0)
