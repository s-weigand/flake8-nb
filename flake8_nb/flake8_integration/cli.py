r"""Module containing the notebook gatherer and hack of flake8.

This is the main implementation of ``flake8_nb``, it relies on
overwriting ``flake8`` 's CLI default options, searching and parsing
``*.ipynb`` files and injecting the parsed files, during the loading
of the CLI argv and config of ``flake8``.
"""
from __future__ import annotations

import logging
import os
import sys
from typing import Any
from typing import Callable

from flake8 import __version__ as flake_version
from flake8 import defaults
from flake8 import utils
from flake8.main.application import Application
from flake8.options import aggregator
from flake8.options import config
from flake8.utils import matches_filename

from flake8_nb import FLAKE8_VERSION_TUPLE
from flake8_nb import __version__
from flake8_nb.parsers.notebook_parsers import NotebookParser

LOG = logging.getLogger(__name__)

defaults.EXCLUDE = (*defaults.EXCLUDE, ".ipynb_checkpoints")


def get_notebooks_from_args(
    args: list[str], exclude: list[str] = ["*.tox/*", "*.ipynb_checkpoints*"]
) -> tuple[list[str], list[str]]:
    """Extract the absolute paths to notebooks.

    The paths are relative to the current directory or
    to the CLI passes files/folder and returned as list.

    Parameters
    ----------
    args : list[str]
        The left over arguments that were not parsed by :attr:`option_manager`
    exclude : list[str]
        File-/Folderpatterns that should be excluded,
        by default ["*.tox/*", "*.ipynb_checkpoints*"]

    Returns
    -------
    tuple[list[str], list[str]]
        List of found notebooks absolute paths.
    """

    def is_notebook(file_path: str, nb_list: list[str], root: str = ".") -> bool:
        """Check if a file is a notebook and appends it to nb_list if it is.

        Parameters
        ----------
        file_path : str
            File to check if it is a notebook
        nb_list : list[str]
            List of notebooks
        root : str
            Root directory, by default "."

        Returns
        -------
        bool
            Whether the given file is a notebook
        """
        file_path = os.path.abspath(os.path.join(root, file_path))
        if os.path.isfile(file_path) and file_path.endswith(".ipynb"):
            nb_list.append(os.path.normcase(file_path))
            return True
        return False

    nb_list: list[str] = []
    if not args:
        args = [os.curdir]
    for index, arg in list(enumerate(args))[::-1]:
        if is_notebook(arg, nb_list):
            args.pop(index)
        for root, _, filenames in os.walk(arg):
            if not matches_filename(  # pragma: no branch
                root,
                patterns=exclude,
                log_message='"%(path)s" has %(whether)sbeen excluded',
                logger=LOG,
            ):
                [is_notebook(filename, nb_list, root) for filename in filenames]

    return args, nb_list


def hack_option_manager_generate_versions(
    generate_versions: Callable[..., str]
) -> Callable[..., str]:
    """Closure to prepend the flake8 version to option_manager.generate_versions .

    Parameters
    ----------
    generate_versions : Callable[..., str]
        option_manager.generate_versions of flake8.options.manager.OptionManager

    Returns
    -------
    Callable[..., str]
        hacked_generate_versions
    """

    def hacked_generate_versions(*args: Any, **kwargs: Any) -> str:
        """Inner wrapper around option_manager.generate_versions.

        Parameters
        ----------
        args: Tuple[Any]
            Arbitrary args
        kwargs: Dict[str, Any]
            Arbitrary kwargs

        Returns
        -------
        str
            Plugin versions string containing flake8
        """
        original_output = generate_versions(*args, **kwargs)
        format_str = "%(name)s: %(version)s"
        additional_output = format_str % {
            "name": "flake8",
            "version": flake_version,
        }
        return f"{additional_output}, {original_output}"

    return hacked_generate_versions


class Flake8NbApplication(Application):  # type: ignore[misc]
    r"""Subclass of ``flake8.main.application.Application``.

    It overwrites the default options and an injection of intermediate parsed
    ``*.ipynb`` files to be checked.
    """

    def __init__(self, program: str = "flake8_nb", version: str = __version__):
        """Hacked initialization of flake8.Application.

        Parameters
        ----------
        program : str
            Application name, by default "flake8_nb"
        version : str
            Application version, by default __version__
        """
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
        self.set_flake8_option(
            "--notebook-cell-format",
            metavar="notebook_cell_format",
            default="{nb_path}#In[{exec_count}]",
            parse_from_config=True,
            help="Template string used to format the filename and cell part of error report.\n"
            "Possible variables which will be replaces 'nb_path', 'exec_count',"
            "'code_cell_count' and 'total_cell_count'. (Default: %default)",
        )
        self.option_manager.generate_versions = hack_option_manager_generate_versions(
            self.option_manager.generate_versions
        )
        if FLAKE8_VERSION_TUPLE < (3, 8, 0):
            self.parse_configuration_and_cli = (  # type: ignore[assignment]
                self.parse_configuration_and_cli_legacy  # type: ignore[assignment]
            )

    def hack_flake8_program_and_version(self, program: str, version: str) -> None:
        """Hack to overwrite the program name and version of flake8.

        This is needed because those values are hard coded at creation of `self.option_manager`.

        Parameters
        ----------
        program : str
            Name of the program
        version : str
            Version of the program
        """
        self.program = program
        self.version = version
        self.option_manager.parser.prog = program
        self.option_manager.parser.version = version
        self.option_manager.program_name = program
        self.option_manager.version = version

    def set_flake8_option(self, long_option_name: str, *args: Any, **kwargs: Any) -> None:
        """Overwrite flake8 options.

        First deletes and than reads an option to `flake8`'s cli options, if it was present.
        If the option wasn't present, it just adds it.


        Parameters
        ----------
        long_option_name : str
            Long name of the flake8 cli option.
        args: Tuple[Any]
            Arbitrary args
        kwargs: Dict[str, Any]
            Arbitrary kwargs

        """
        is_option = False
        for option_index, option in enumerate(self.option_manager.options):
            if option.long_option_name == long_option_name:
                self.option_manager.options.pop(option_index)
                is_option = True
        if is_option:
            # pylint: disable=no-member
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
        """Overwrite ``flake8``'s default options, with ``flake8_nb`` defaults."""
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

    @staticmethod
    def hack_args(args: list[str], exclude: list[str]) -> list[str]:
        r"""Update args with ``*.ipynb`` files.

        Checks the passed args if ``*.ipynb`` can be found and
        appends intermediate parsed files to the list of files,
        which should be checked.

        Parameters
        ----------
        args : list[str]
            List of commandline arguments provided to ``flake8_nb``
        exclude : list[str]
            File-/Folderpatterns that should be excluded

        Returns
        -------
        list[str]
            The original args + intermediate parsed ``*.ipynb`` files.
        """
        args, nb_list = get_notebooks_from_args(args, exclude=exclude)
        notebook_parser = NotebookParser(nb_list)
        return args + notebook_parser.intermediate_py_file_paths

    def parse_configuration_and_cli_legacy(
        self,
        argv: list[str] | None = None,
    ) -> None:
        """Compat version of self.parse_configuration_and_cli to work with flake8 >=3.7.0,<= 3.7.9 .

        See https://gitlab.com/pycqa/flake8/blob/master/src/flake8/main/application.py#L194

        Parse configuration files and the CLI options.

        Parameters
        ----------
        argv: list[str] | None
            Command-line arguments passed in directly.
        """
        if self.options is None and self.args is None:  # type: ignore  # pragma: no branch
            # pylint: disable=no-member
            self.options, self.args = aggregator.aggregate_options(
                self.option_manager, self.config_finder, argv
            )

        self.args = self.hack_args(self.args, self.options.exclude)

        self.running_against_diff = self.options.diff
        if self.running_against_diff:  # pragma: no cover
            self.parsed_diff = utils.parse_unified_diff()
            if not self.parsed_diff:
                self.exit()

        self.options._running_from_vcs = False

        self.check_plugins.provide_options(self.option_manager, self.options, self.args)
        self.formatting_plugins.provide_options(self.option_manager, self.options, self.args)

    def parse_configuration_and_cli(
        self, config_finder: config.ConfigFileFinder, argv: list[str]
    ) -> None:
        """Parse configuration files and the CLI options.

        Parameters
        ----------
        config_finder: config.ConfigFileFinder
            The finder for finding and reading configuration files.
        argv: list[str]
            Command-line arguments passed in directly.
        """
        self.options, self.args = aggregator.aggregate_options(
            self.option_manager,
            config_finder,
            argv,
        )

        self.args = self.hack_args(self.args, self.options.exclude)

        self.running_against_diff = self.options.diff
        if self.running_against_diff:  # pragma: no cover
            self.parsed_diff = utils.parse_unified_diff()
            if not self.parsed_diff:
                self.exit()

        self.options._running_from_vcs = False

        self.check_plugins.provide_options(self.option_manager, self.options, self.args)
        self.formatting_plugins.provide_options(self.option_manager, self.options, self.args)

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
