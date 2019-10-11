import logging
import os

from typing import List, Optional, Tuple

from flake8 import utils, defaults
from flake8.options import aggregator
from flake8.main.application import Application
from flake8.utils import matches_filename

from .. import __version__

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

    nb_list = []
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
    def __init__(self, program="flake8_nb", version=__version__):
        super().__init__(program, version)
        self.cleaned_args = []
        self.overwrite_flake8_program_and_version(program, version)
        self.overwrite_flake8_option(
            "--format",
            metavar="format",
            default="default_notebook",
            parse_from_config=True,
            help="Format errors according to the chosen formatter.",
        )
        self.overwrite_flake8_option(
            "--filename",
            metavar="patterns",
            default="*.py,*.ipynb_parsed",
            parse_from_config=True,
            comma_separated_list=True,
            help="Only check for filenames matching the patterns in this comma-"
            "separated list. (Default: %default)",
        )
        self.overwrite_flake8_option(
            "--exclude",
            metavar="patterns",
            default=f'{",".join(defaults.EXCLUDE)},*.ipynb_checkpoints/*',
            comma_separated_list=True,
            parse_from_config=True,
            normalize_paths=True,
            help="Comma-separated list of files or directories to exclude."
            " (Default: %default)",
        )

    def overwrite_flake8_program_and_version(self, program: str, version: str):
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
        self.option_manager.parser.prog = program
        self.option_manager.parser.version = version
        self.option_manager.program_name = program
        self.option_manager.version = version

    def overwrite_flake8_option(self, long_option_name: str, *args, **kwargs):
        """
        First deletes and than adds an option to flake8's cli options

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
            self.option_manager.parser.remove_option(long_option_name)
            self.option_manager.add_option(long_option_name, *args, **kwargs)

    @staticmethod
    def hack_args(args: List[str]):

        args, nb_list = get_notebooks_from_args(args)
        notebook_parser = NotebookParser(nb_list)
        return args + notebook_parser.intermediate_py_file_paths

    def parse_configuration_and_cli(self, argv=None):
        # type: (Optional[List[str]]) -> None
        """Parse configuration files and the CLI options.

        :param list argv:
            Command-line arguments passed in directly.
        """
        if self.options is None and self.args is None:
            self.options, self.args = aggregator.aggregate_options(
                self.option_manager, self.config_finder, argv
            )

        self.args = self.hack_args(self.args)

        self.running_against_diff = self.options.diff
        if self.running_against_diff:
            self.parsed_diff = utils.parse_unified_diff()
            if not self.parsed_diff:
                self.exit()

        self.options._running_from_vcs = False

        self.check_plugins.provide_options(self.option_manager, self.options, self.args)
        self.formatting_plugins.provide_options(
            self.option_manager, self.options, self.args
        )

    def initialize(self, argv: List[str]) -> None:
        super().initialize(argv)

    def exit(self):
        # type: () -> None
        """Handle finalization and exiting the program.

        This should be the last thing called on the application instance. It
        will check certain options and exit appropriately.
        """
        NotebookParser.clean_up()
        super().exit()
