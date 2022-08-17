r"""Module containing the notebook gatherer and hack of flake8.

This is the main implementation of ``flake8_nb``, it relies on
overwriting ``flake8`` 's CLI default options, searching and parsing
``*.ipynb`` files and injecting the parsed files, during the loading
of the CLI argv and config of ``flake8``.
"""
from __future__ import annotations

import configparser
import logging
import os
import sys
from pathlib import Path
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


def hack_config_module() -> None:
    """Create hacked version of ``flake8.options.config`` at runtime.

    Since flake8>=5.0.0 uses hardcoded ``"flake8"`` to discover the config we replace
    with it with ``"flake8_nb"`` to create our own hacked version and replace
    the references to the original module with the hacked one.

    See:
        https://github.com/s-weigand/flake8-nb/issues/249
        https://github.com/s-weigand/flake8-nb/issues/254
    """
    hacked_config_source = (
        Path(config.__file__)
        .read_text()
        .replace('"flake8"', '"flake8_nb"')
        .replace('".flake8"', '".flake8_nb"')
    )
    hacked_config_path = Path(__file__).parent / "hacked_config.py"
    hacked_config_path.write_text(hacked_config_source)

    from flake8_nb.flake8_integration import hacked_config  # type:ignore[attr-defined]

    sys.modules["flake8.options.config"] = hacked_config
    aggregator.config = hacked_config

    import flake8.main.application as application_module

    application_module.config = hacked_config


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
        super().__init__()
        if FLAKE8_VERSION_TUPLE < (5, 0, 0):
            self.apply_hacks()
            self.option_manager.generate_versions = hack_option_manager_generate_versions(
                self.option_manager.generate_versions
            )
            self.parse_configuration_and_cli = (  # type: ignore[assignment]
                self.parse_configuration_and_cli_legacy  # type: ignore[assignment]
            )
        else:
            hack_config_module()
            self.register_plugin_options = self.hacked_register_plugin_options

    def apply_hacks(self) -> None:
        """Apply hacks to flake8 adding options and changing the application name + version."""
        self.hack_flake8_program_and_version("flake8_nb", __version__)
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

    def hacked_register_plugin_options(self) -> None:
        """Register options provided by plugins to our option manager."""
        assert self.plugins is not None
        from flake8.main import options
        from flake8.options import manager

        plugin_version = ", ".join(
            [v for v in self.plugins.versions_str().split(", ") if not v.startswith("flake8-nb")]
        )

        self.option_manager = manager.OptionManager(
            version=__version__,
            plugin_versions=f"flake8: {flake_version}, {plugin_version}",
            parents=[self.prelim_arg_parser],
        )
        options.register_default_options(self.option_manager)
        self.option_manager.register_plugins(self.plugins)

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
            for index, action in enumerate(parser._actions):  # pragma: no branch
                if long_option_name in action.option_strings:
                    parser._handle_conflict_resolve(
                        None, [(long_option_name, parser._actions[index])]
                    )
                    break
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

    def parse_configuration_and_cli(
        self,
        cfg: configparser.RawConfigParser,
        cfg_dir: str,
        argv: list[str],
    ) -> None:
        """
        Parse configuration files and the CLI options.

        Parameters
        ----------
        cfg: configparser.RawConfigParser
            Config parser instance
        cfg_dir: str
            Dir the the config is in.
        argv: list[str]
            CLI args

        Raises
        ------
        SystemExit
            If ``--bug-report`` option is passed to the CLI.
        """
        assert self.option_manager is not None
        assert self.plugins is not None

        self.apply_hacks()

        self.options = aggregator.aggregate_options(
            self.option_manager,
            cfg,
            cfg_dir,
            argv,
        )

        argv = self.hack_args(argv, self.options.exclude)

        self.options = aggregator.aggregate_options(
            self.option_manager,
            cfg,
            cfg_dir,
            argv,
        )

        import json

        from flake8.main import debug

        if self.options.bug_report:
            info = debug.information(__version__, self.plugins)
            for index, plugin in enumerate(info["plugins"]):
                if plugin["plugin"] == "flake8-nb":
                    del info["plugins"][index]
            info["flake8-version"] = flake_version
            print(json.dumps(info, indent=2, sort_keys=True))
            raise SystemExit(0)

        if self.options.diff:  # pragma: no cover
            LOG.warning(
                "the --diff option is deprecated and will be removed in a " "future version."
            )
            self.parsed_diff = utils.parse_unified_diff()

        for loaded in self.plugins.all_plugins():
            parse_options = getattr(loaded.obj, "parse_options", None)
            if parse_options is None:
                continue

            # XXX: ideally we wouldn't have two forms of parse_options
            try:
                parse_options(
                    self.option_manager,
                    self.options,
                    self.options.filenames,
                )
            except TypeError:
                parse_options(self.options)

    def exit(self) -> None:
        """Handle finalization and exiting the program.

        This should be the last thing called on the application instance. It
        will check certain options and exit appropriately.

        Raises
        ------
        SystemExit
            For flake8>=5.0.0
        """
        if self.options.keep_parsed_notebooks:
            temp_path = NotebookParser.temp_path
            print(
                f"The parsed notebooks, are still present at:\n\t{temp_path}",
                file=sys.stderr,
            )
        else:
            NotebookParser.clean_up()
        if FLAKE8_VERSION_TUPLE < (5, 0, 0):
            super().exit()
        else:
            raise SystemExit(self.exit_code())
