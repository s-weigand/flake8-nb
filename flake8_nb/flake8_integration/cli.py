import argparse
import logging
import os

from typing import List, Optional, Tuple, Union

from flake8.main.application import Application
from flake8.utils import matches_filename

from .. import __version__, FLAKE8_VERSION_TUPLE

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
            nb_list.append(filename)
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

    def _run(self, argv: Optional[List[str]]) -> None:
        self.initialize(argv)
        self.run_checks(self.prelim_args)
        self.report()

    def parse_preliminary_options_and_args(
        self, argv: Union[None, List[str]]
    ) -> Union[None, Tuple[argparse.Namespace, List[str]]]:
        """
        Get preliminary options and args from CLI, pre-plugin-loading.

        We need to know the values of a few standard options and args now, so
        that we can find config files and configure logging.

        Since plugins aren't loaded yet, there may be some as-yet-unknown
        options; we ignore those for now, they'll be parsed later when we do
        real option parsing.

        Sets self.prelim_opts and self.prelim_args.

        Parameters
        ----------
        argv : Union[None, List[str]]
            Command-line arguments passed in directly.

        Returns
        -------
        Union[None, Tuple[argparse.Namespace, List[str]]]
            [description]
        """
        if FLAKE8_VERSION_TUPLE > (3, 7, 8):
            # compat for code after b54164f (flake8>3.7.8)
            # see https://github.com/PyCQA/flake8/commit/b54164f916922725c17e6d0df75998ada6b27eef#diff-d5a0050fc6e4a3978782bdca39900c59  # noqa
            # pylint: disable=assignment-from-no-return
            prelim_opts, prelim_args = super().parse_preliminary_options_and_args(argv)
            # print(prelim_opts, prelim_args)
            args, nb_list = get_notebooks_from_args(prelim_args)
            notebook_parser = NotebookParser(nb_list)
            total_args = args + notebook_parser.intermediate_py_file_paths
            return prelim_opts, total_args

        else:
            # TODO: remove compat after flake8>3.7.8 release
            super().parse_preliminary_options_and_args(argv)
            args, nb_list = get_notebooks_from_args(self.prelim_args)
            notebook_parser = NotebookParser(nb_list)
            total_args = args + notebook_parser.intermediate_py_file_paths
            print(total_args)
            self.prelim_args = total_args
            # print(self.prelim_opts, self.prelim_args)
        self.cleaned_args = args

    def initialize(self, argv: List[str]) -> None:
        super().initialize(argv)
        print("self.args", self.args)

    def exit(self):
        # type: () -> None
        """Handle finalization and exiting the program.

        This should be the last thing called on the application instance. It
        will check certain options and exit appropriately.
        """
        NotebookParser.clean_up()
        super().exit()
