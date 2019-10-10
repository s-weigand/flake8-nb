import optparse
import os

from flake8.formatting.default import Default
from flake8.style_guide import Violation

from ..parsers.notebook_parsers import NotebookParser, map_intermediate_to_input


class IpynbFormatter(Default):
    """
    Default flake8 formatter for jupyter notebooks.
    If the file to be formated is a *.py file,
    it uses flake8's default formatter.
    """

    def __init__(self, options: optparse.Values) -> None:
        super().__init__(options)
        print(f" USING ##### { IpynbFormatter }")

    def after_init(self):  # type: () -> None
        """Check for a custom format string."""
        if self.options.format.lower() != "default_notebook":
            self.error_format = self.options.format

    def format(self, error: Violation):
        filename = error.filename
        if filename.lower().endswith(".py"):
            return super().format(error)
        elif filename.lower().endswith(".ipynb_parsed"):
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

    def map_notebook_error(self, error: Violation):
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
