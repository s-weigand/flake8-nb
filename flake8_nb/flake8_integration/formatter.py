import optparse

from flake8.formatting.default import Default
from flake8.style_guide import Violation

from ..parsers.notebook_parsers import NotebookParser


class IpynbFormatter(Default):
    """
    Default flake8 formatter for jupyter notebooks.
    If the file to be formated is a *.py file,
    it uses flake8's default formatter.
    """

    def __init__(self, options: optparse.Values) -> None:
        super().__init__(options)
        self.notebook_parser = NotebookParser()

    def format(self, error: Violation):
        print(f" USING ##### { IpynbFormatter }")
        filename = error.filename
        if filename.lower().endswith(".py"):
            return super().format(error)
        elif filename.lower().endswith(".ipynb"):
            return f"NOTEBOOK at: {filename}"
