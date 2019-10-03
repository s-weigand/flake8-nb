import argparse
import logging
from typing import List, Tuple, Union

from flake8.main.application import Application
from flake8.formatting.default import Default

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
        self.overwrite_flake8_option(
            "--format",
            metavar="format",
            default="default_notebook",
            parse_from_config=True,
            help="Format errors according to the chosen formatter.",
        )

    def overwrite_flake8_option(self, long_option_name: str, *args, **kwargs):
        for option_index, option in enumerate(self.option_manager.options):
            if option.long_option_name == long_option_name:
                self.option_manager.options.pop(option_index)
        self.option_manager.parser.remove_option(long_option_name)
        self.option_manager.add_option(long_option_name, *args, **kwargs)

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

    def initialize(self, argv: List[str]) -> None:
        super().initialize(argv)
        print("self.args", self.args)
