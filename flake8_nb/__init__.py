"""Top-level package for flake8-nb."""

__author__ = """Sebastian Weigand"""
__email__ = "s.weigand.phy@gmail.com"
__version__ = "0.4.0"

import flake8

from flake8_nb.flake8_integration.formatter import IpynbFormatter

__all__ = [
    IpynbFormatter.__name__,
]


def save_cast_int(int_str: str) -> int:
    """Cast version string to tuple, in a save manner.

    This is needed so the version number of prereleases (i.e. 3.8.0rc1)
    don't not throw exceptions.

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
