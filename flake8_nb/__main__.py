"""Command-line implementation of flake8_nb."""
from __future__ import annotations

import sys

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
    app = Flake8NbApplication()
    app.run(sys.argv[1:] if argv is None else argv[1:])
    app.exit()


if __name__ == "__main__":
    main()
