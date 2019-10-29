# -*- coding: utf-8 -*-

r"""Module containing the notebook gatherer and hack of flake8.
This is the main implementation of ``flake8_nb``, it relies on
overwriting ``flake8`` 's CLI default options, searching and parsing
``*.ipynb`` files and injecting the parsed files, during the loading
of the CLI argv and config of ``flake8``.
"""

import logging
import os
import sys
from typing import List, Optional, Tuple

from flake8 import defaults, utils
from flake8.main.application import Application
from flake8.options import aggregator
from flake8.utils import matches_filename

from .. import FLAKE8_VERSION_TUPLE, __version__
from ..parsers.notebook_parsers import NotebookParser

LOG = logging.getLogger(__name__)


def get_notebooks_from_args(
    args: List[str], exclude: List[str] = ["*.tox/*", "*.ipynb_checkpoints*"]
) -> Tuple[List[str], List[str]]:
    """
    Extracts the absolute paths to notebooks from current director or
    the to the CLI passes files/folder and return the as list.

    Parameters
    ----------
    args : List[str]
        The left over arguments that were not parsed by :attr:`option_manager`
    exclude : List[str], optional
        File-/Folderpatterns that should be excluded, by default ["*.tox/*"]

    Returns
    -------
    Tuple[List[str],List[str]]
        List of found notebooks absolute paths.
    """

    def is_notebook(filename: str, nb_list: List, root="."):
        filename = os.path.abspath(os.path.join(root, filename))
        if os.path.isfile(filename) and filename.endswith(".ipynb"):
            nb_list.append(os.path.normcase(filename))
            return True

    nb_list: List[str] = []
    if not args:
        args = [os.curdir]
    for index, arg in list(enumerate(args))[::-1]:
        if is_notebook(arg, nb_list):
            args.pop(index)
        for root, _, filenames in os.walk(arg):
            if not matches_filename(
                root,
                patterns=exclude,
                log_message='"%(path)s" has %(whether)sbeen excluded',
                logger=LOG,
            ):
                [is_notebook(filename, nb_list, root) for filename in filenames]

    return args, nb_list


class Flake8NbApplication(Application):
    r"""
    Subclass of ```flake8.main.application.Application``, with
    overwritten default options and an injection of intermediate parsed
    ``*.ipynb`` files to be checked.
    """

    def __init__(self, program="flake8_nb", version=__version__):
        super().__init__(program, version)
        self.hack_flake8_program_and_version(program, version)
        self.hack_options()
        self.set_flake8_option(
            "--keep-parsed-notebooks",
            default=False,
            action="store_true",
            parse_from_config=True,
            help="Keep the temporary parsed notebooks, i.e. for debugging.",
        )

    def hack_flake8_program_and_version(self, program: str, version: str) -> None:
        """
        Another hack to overwrite the program name and version of flake8,
        which is hard coded at creation of `self.option_manager`.

        Parameters
        ----------
        program : str
            Name of the program
        version : str
            Version of the program
        """
        # TODO Cleanup after flake8>3.7.8 release
        # if https://gitlab.com/pycqa/flake8/merge_requests/359#note_226407899 gets merged
        self.program = program
        self.version = version
        self.option_manager.parser.prog = program
        self.option_manager.parser.version = version
        self.option_manager.program_name = program
        self.option_manager.version = version

    def set_flake8_option(self, long_option_name: str, *args, **kwargs) -> None:
        """
        First deletes and than readds an option to `flake8`'s cli options, if it was present.
        If the option wasn't present, it just adds it.


        Parameters
        ----------
        long_option_name : str
            Long name of the flake8 cli option.
        """
        is_option = False
        for option_index, option in enumerate(self.option_manager.options):
            if option.long_option_name == long_option_name:
                self.option_manager.options.pop(option_index)
                is_option = True
        if is_option:
            parser = self.option_manager.parser
            if FLAKE8_VERSION_TUPLE > (3, 7, 9):
                for index, action in enumerate(parser._actions):  # pragma: no branch
                    if long_option_name in action.option_strings:
                        parser._handle_conflict_resolve(
                            None, [(long_option_name, parser._actions[index])]
                        )
                        break
            else:
                parser.remove_option(long_option_name)
        self.option_manager.add_option(long_option_name, *args, **kwargs)

    def hack_options(self) -> None:
        """
        Overwrites ``flake8``'s default options, with ``flake8_nb`` defaults.
        """
        self.set_flake8_option(
            "--format",
            metavar="format",
            default="default_notebook",
            parse_from_config=True,
            help="Format errors according to the chosen formatter.",
        )
        self.set_flake8_option(
            "--filename",
            metavar="patterns",
            default="*.py,*.ipynb_parsed",
            parse_from_config=True,
            comma_separated_list=True,
            help="Only check for filenames matching the patterns in this comma-"
            "separated list. (Default: %default)",
        )
        self.set_flake8_option(
            "--exclude",
            metavar="patterns",
            default=f'{",".join(defaults.EXCLUDE)},*.ipynb_checkpoints/*',
            comma_separated_list=True,
            parse_from_config=True,
            normalize_paths=True,
            help="Comma-separated list of files or directories to exclude."
            " (Default: %default)",
        )

    @staticmethod
    def hack_args(args: List[str]) -> List[str]:
        r"""
        Checks the passed args if ``*.ipynb`` can be found and
        appends intermediate parsed files to the list of files,
        which should be checked.

        Parameters
        ----------
        args : List[str]
            List of commandline arguments provided to ``flake8_nb``

        Returns
        -------
        List[str]
            The original args + intermediate parsed ``*.ipynb`` files.
        """

        args, nb_list = get_notebooks_from_args(args)
        notebook_parser = NotebookParser(nb_list)
        return args + notebook_parser.intermediate_py_file_paths

    def parse_configuration_and_cli(self, argv: Optional[List[str]] = None) -> None:
        """
        Parse configuration files and the CLI options.

        Parameters
        ----------
        argv: List[str]
            Command-line arguments passed in directly.
        """
        if self.options is None and self.args is None:  # pragma: no branch
            self.options, self.args = aggregator.aggregate_options(
                self.option_manager, self.config_finder, argv
            )

        self.args = self.hack_args(self.args)

        self.running_against_diff = self.options.diff
        if self.running_against_diff:  # pragma: no cover
            self.parsed_diff = utils.parse_unified_diff()
            if not self.parsed_diff:
                self.exit()

        self.options._running_from_vcs = False

        self.check_plugins.provide_options(self.option_manager, self.options, self.args)
        self.formatting_plugins.provide_options(
            self.option_manager, self.options, self.args
        )

    def exit(self) -> None:
        """Handle finalization and exiting the program.

        This should be the last thing called on the application instance. It
        will check certain options and exit appropriately.
        """
        if self.options.keep_parsed_notebooks:
            temp_path = NotebookParser.temp_path
            print(
                f"The parsed notebooks, are still present at:\n\t{temp_path}",
                file=sys.stderr,
            )
        else:
            NotebookParser.clean_up()
        super().exit()
