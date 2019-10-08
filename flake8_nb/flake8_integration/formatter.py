from flake8.formatting.default import Default

from flake8.style_guide import Violation


class IpynbFormater(Default):
    """
    Default flake8 formatter for jupyter notebooks.
    If the file to be formated is a *.py file,
    it uses flake8's default formatter.
    """

    def format(self, error: Violation):
        print(f" USING ##### { IpynbFormater }")
        filename = error.filename
        if filename.lower().endswith(".py"):
            return super().format(error)
        elif filename.lower().endswith(".ipynb"):
            return "NOTEBOOK"
