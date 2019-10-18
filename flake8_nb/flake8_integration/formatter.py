# -*- coding: utf-8 -*-

"""Module containing the report formatter.
This also includes the code to map parsed error back to the
original notebook and the cell the code in."""

import optparse
import os
from typing import Tuple

from flake8.formatting.default import Default
from flake8.style_guide import Violation

from ..parsers.notebook_parsers import NotebookParser, map_intermediate_to_input


class IpynbFormatter(Default):
    r"""
    Default flake8_nb formatter for jupyter notebooks.
    If the file to be formated is a ``*.py`` file,
    it uses flake8's default formatter.
    """

    def __init__(self, options: optparse.Values) -> None:
        super().__init__(options)

    def after_init(self):  # type: () -> None
        """Check for a custom format string."""
        if self.options.format.lower() != "default_notebook":
            self.error_format = self.options.format

    def format(self, error: Violation) -> str:
        r"""
        Formats the error detected by a flake8 checker,
        depending on if the error was caused by a ``*.py`` file
        or by a parsed notebook.

        Parameters
        ----------
        error : Violation
            Error a checker reported.

        Returns
        -------
        str
            Formatted error message, which will be displayed
            in the terminal.
        """
        filename = error.filename
        if filename.lower().endswith(".ipynb_parsed"):
            map_result = self.map_notebook_error(error)
            if map_result:
                filename, line_number = self.map_notebook_error(error)
                return self.error_format % {
                    "code": error.code,
                    "text": error.text,
                    "path": filename,
                    "row": line_number,
                    "col": error.column_number,
                }

            return super().format(error)
        else:
            return super().format(error)

    def map_notebook_error(self, error: Violation) -> Tuple[str, int]:
        """
        Maps the error caused by an intermediate file back
        to a notebook, the input cell it caused and the
        respective line number in that cell.

        Parameters
        ----------
        error : Violation
            Reported error from checking the parsed notebook

        Returns
        -------
        Tuple[str, int]
            (filename, input_cell_line_number)
            ``filename`` being the name of the original notebook and
            the input cell were the error was reported.
            ``input_cell_line_number`` line number in the input cell
            were the error was reported.
        """
        intermediate_filename = os.path.abspath(error.filename)
        intermediate_line_number = error.line_number
        mappings = NotebookParser.get_mappings()
        for original_notebook, intermediate_py, input_line_mapping in mappings:
            if os.path.samefile(intermediate_py, intermediate_filename):
                input_cell_name, input_cell_line_number = map_intermediate_to_input(
                    input_line_mapping, intermediate_line_number
                )
                filename = f"{original_notebook}#{input_cell_name}"
                return filename, input_cell_line_number
