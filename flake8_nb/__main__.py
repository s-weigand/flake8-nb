"""Command-line implementation of flake8."""
import sys
from typing import List

from flake8_nb.flake8_integration import Flake8NbApplication

from flake8_nb import FLAKE8_VERSION_TUPLE


def main(argv=None):
    # type: (Optional[List[str]]) -> None
    """Execute the main bit of the application.
    This handles the creation of an instance of :class:`Application`, runs it,
    and then exits the application.
    :param list argv:
        The arguments to be passed to the application for parsing.
    """
    # TODO: remove compat after flake8>3.7.8 release
    if FLAKE8_VERSION_TUPLE > (3, 7, 8):
        if argv is None:
            argv = sys.argv[1:]

    app = Flake8NbApplication()
    app.run(argv)
    app.exit()
