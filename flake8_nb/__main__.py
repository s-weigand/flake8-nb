"""Command-line implementation of flake8_nb."""
from __future__ import annotations

import sys

from flake8_nb import FLAKE8_VERSION_TUPLE
from flake8_nb.flake8_integration.cli import Flake8NbApplication


def main(argv: list[str] | None = None) -> None:
    """Execute the main bit of the application.

    This handles the creation of an instance of :class:`Application`, runs it,
    and then exits the application.


    Parameters
    ----------
    argv: list[str] | None
        The arguments to be passed to the application for parsing.
    """
    if FLAKE8_VERSION_TUPLE > (3, 7, 9):
        argv = sys.argv[1:] if argv is None else argv[1:]
    app = Flake8NbApplication()
    app.run(argv)
    app.exit()
