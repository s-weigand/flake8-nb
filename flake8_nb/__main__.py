"""Command-line implementation of flake8_nb."""
import sys
from typing import List
from typing import Optional

from flake8_nb import FLAKE8_VERSION_TUPLE
from flake8_nb.flake8_integration.cli import Flake8NbApplication


def main(argv: Optional[List[str]] = None) -> None:
    """Execute the main bit of the application.

    This handles the creation of an instance of :class:`Application`, runs it,
    and then exits the application.


    Parameters
    ----------
    argv: List[str], optional
        The arguments to be passed to the application for parsing.
    """
    # TODO: remove compat after flake8>3.8.0 release
    # tested with flake8-nightly, in test__main__.py,
    # but not picked up by by coverage
    if FLAKE8_VERSION_TUPLE > (3, 7, 9):  # pragma: no cover
        if argv is None:
            argv = sys.argv[1:]
        else:
            argv = argv[1:]

    app = Flake8NbApplication()
    app.run(argv)
    app.exit()
