import argparse
import logging
import os
from typing import List, Tuple, Union

from flake8 import utils
from flake8.main.application import Application
from flake8.main import options
from flake8.formatting.default import Default
from flake8.options import manager, config

from flake8.style_guide import Violation

from . import __version__, FLAKE8_VERSION_TUPLE

LOG = logging.getLogger(__name__)


class IpynbFormater(Default):
    def format(self, error: Violation):
        print(f" USING ##### { IpynbFormater }")
        filename = error.filename
        if filename.lower().endswith(".py"):
            return super().format(error)
        elif filename.lower().endswith(".ipynb"):
            return "NOTEBOOK"


class Flake8NbApplication(Application):
    def __init__(self, program="flake8_nb", version=__version__):
        super().__init__(program, version)
        #: The instance of :class:`flake8.options.manager.OptionManager` used
        #: to parse and handle the options and arguments passed by the user
        self.option_manager = manager.OptionManager(prog=program, version=version)
        options.register_default_options(self.option_manager)

    def make_config_finder(
        self,
        append_config: Union[None, List[str]] = None,
        args: Union[None, List[str]] = None,
    ):
        """Make our ConfigFileFinder based on preliminary opts and args.
        :param list append_config:
            List of configuration files to be parsed for configuration.
        :param list args:
            The list of file arguments passed from the CLI.
        """
        coustom_config_path = os.path.abspath(
            os.path.join(os.path.dirname(__name__), "custom_config.ini")
        )
        print(coustom_config_path)
        if self.config_finder is None:
            if FLAKE8_VERSION_TUPLE > (3, 7, 8):
                append_config.insert(0, coustom_config_path)
                self.config_finder = config.ConfigFileFinder(
                    self.option_manager.program_name, args, append_config
                )
            else:
                # TODO: remove compat after flake8>3.7.8 release
                print(type(self.prelim_opts))
                append_config = self.prelim_opts.append_config or []
                append_config.insert(0, coustom_config_path)
                extra_config_files = utils.normalize_paths(append_config)
                print(extra_config_files)
                self.config_finder = config.ConfigFileFinder(
                    self.option_manager.program_name,
                    self.prelim_args,
                    extra_config_files,
                )

    def parse_preliminary_options_and_args(
        self, argv: Union[None, List[str]]
    ) -> Union[None, Tuple[argparse.Namespace, List[str]]]:
        if FLAKE8_VERSION_TUPLE > (3, 7, 8):
            # compat for code after b54164f (flake8>3.7.8)
            # see https://github.com/PyCQA/flake8/commit/b54164f916922725c17e6d0df75998ada6b27eef#diff-d5a0050fc6e4a3978782bdca39900c59  # noqa
            prelim_opts, prelim_args = super().parse_preliminary_options_and_args(argv)
            # print(prelim_opts, prelim_args)

        else:
            # TODO: remove compat after flake8>3.7.8 release
            super().parse_preliminary_options_and_args(argv)
            # print(self.prelim_opts, self.prelim_args)

    # def formatter_for(self, formatter_plugin_name):
    #     """Retrieve the formatter class by plugin name."""
    #     default_formatter = self.formatting_plugins["default_notebook"]
    #     # print("default_formatter", default_formatter)
    #     formatter_plugin = self.formatting_plugins.get(formatter_plugin_name)
    #     # print("formatter_plugin", formatter_plugin)
    #     if formatter_plugin is None:
    #         LOG.warning(
    #             '"%s" is an unknown formatter. Falling back to default.',
    #             formatter_plugin_name,
    #         )
    #         formatter_plugin = default_formatter

    #     print("formatter_plugin", formatter_plugin)
    #     print(self.options)

    #     return default_formatter.execute

    def initialize(self, argv: List[str]) -> None:
        super().initialize(argv)
        print("self.args", self.args)

    #     if hasattr(self, "prelim_opts") and hasattr(self, "prelim_opts"):
    #         super().initialize(argv)
    #         print(self.prelim_opts, self.prelim_args)
    #     else:
    #         # compat for code after b54164f (flake8>3.7.8)
    #         # see https://github.com/PyCQA/flake8/commit/b54164f916922725c17e6d0df75998ada6b27eef#diff-d5a0050fc6e4a3978782bdca39900c59  # noqa
    #         prelim_opts, prelim_args = self.parse_preliminary_options_and_args(argv)
    #         flake8.configure_logging(prelim_opts.verbose, prelim_opts.output_file)
    #         self.make_config_finder(prelim_opts.append_config, prelim_args)
    #         self.find_plugins(prelim_opts.config, prelim_opts.isolated)
    #         self.register_plugin_options()
    #         self.parse_configuration_and_cli(argv)
    #         self.make_formatter()
    #         self.make_guide()
    #         self.make_file_checker_manager()
