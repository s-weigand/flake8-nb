"""Module containing the report formatter.

This also includes the code to map parsed error back to the
original notebook and the cell the code in.
"""

import os
from typing import Tuple
from typing import Union

from flake8.formatting.default import Default
from flake8.style_guide import Violation

from ..parsers.notebook_parsers import NotebookParser
from ..parsers.notebook_parsers import map_intermediate_to_input


def map_notebook_error(violation: Violation) -> Union[Tuple[str, int], None]:
    """Map the violation caused in an intermediate file back to its cause.

    The cause is resolved as the notebook, the input cell and
    the respective line number in that cell.

    Parameters
    ----------
    violation : Violation
        Reported violation from checking the parsed notebook

    Returns
    -------
    Tuple[str, int]
        (filename, input_cell_line_number)
        ``filename`` being the name of the original notebook and
        the input cell were the violation was reported.
        ``input_cell_line_number`` line number in the input cell
        were the violation was reported.
    """
    intermediate_filename = os.path.abspath(violation.filename)
    intermediate_line_number = violation.line_number
    mappings = NotebookParser.get_mappings()
    for original_notebook, intermediate_py, input_line_mapping in mappings:
        if os.path.samefile(intermediate_py, intermediate_filename):
            input_cell_name, input_cell_line_number = map_intermediate_to_input(
                input_line_mapping, intermediate_line_number
            )
            filename = f"{original_notebook}#{input_cell_name}"
            return filename, input_cell_line_number


class IpynbFormatter(Default):
    r"""Default flake8_nb formatter for jupyter notebooks.

    If the file to be formatted is a ``*.py`` file,
    it uses flake8's default formatter.
    """

    def after_init(self) -> None:
        """Check for a custom format string."""
        if self.options.format.lower() != "default_notebook":
            self.error_format = self.options.format

    def format(self, violation: Violation) -> str:
        r"""Format the error detected by a flake8 checker.

        Depending on if the violation was caused by a ``*.py`` file
        or by a parsed notebook.

        Parameters
        ----------
        violation : Violation
            Error a checker reported.

        Returns
        -------
        str
            Formatted error message, which will be displayed
            in the terminal.
        """
        filename = violation.filename
        if filename.lower().endswith(".ipynb_parsed"):
            map_result = map_notebook_error(violation)
            if map_result:
                filename, line_number = map_result
                return self.error_format % {
                    "code": violation.code,
                    "text": violation.text,
                    "path": filename,
                    "row": line_number,
                    "col": violation.column_number,
                }

            return super().format(violation)
        else:
            return super().format(violation)
