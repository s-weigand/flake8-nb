# -*- coding: utf-8 -*-

import os
from typing import Tuple

import pytest

from ..parsers.test_notebook_parsers import notebook_parser

from flake8_nb.flake8_integration.formatter import IpynbFormatter
from flake8_nb.parsers.notebook_parsers import NotebookParser


class MockedOption:
    output_file = ""
    format = "default_notebook"


class MockError:
    def __init__(self, filename: str, line_number: int):
        self.filename = os.path.normpath(filename)
        self.line_number = line_number


@pytest.mark.parametrize(
    "line_number,expected_input_number,expected_line_number",
    [(8, 1, 2), (15, 2, 2), (29, 4, 2), (30, 4, 3), (38, 5, 3)],
)
def test_IpynbFormatter__map_notebook_error(
    notebook_parser: NotebookParser,
    line_number: int,
    expected_input_number: int,
    expected_line_number: int,
):
    formatter = IpynbFormatter(MockedOption)
    expected_filename = os.path.join(
        "tests",
        "data",
        "notebooks",
        f"notebook_with_flake8_tags.ipynb#In[{expected_input_number}]",
    )
    intermediate_names = notebook_parser.intermediate_py_file_paths
    filename = [
        filename
        for filename in intermediate_names
        if filename.endswith("notebook_with_flake8_tags.ipynb_parsed")
    ][0]
    mock_error = MockError(filename, line_number)
    filename, input_cell_line_number = formatter.map_notebook_error(mock_error)
    assert input_cell_line_number == expected_line_number
    assert filename == expected_filename
