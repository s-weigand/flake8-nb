import os
from optparse import Values
from typing import List

import pytest
from flake8.style_guide import Violation

from flake8_nb.flake8_integration.formatter import IpynbFormatter
from flake8_nb.flake8_integration.formatter import map_notebook_error
from flake8_nb.parsers.notebook_parsers import NotebookParser

TEST_NOTEBOOK_PATH = os.path.join("tests", "data", "notebooks", "notebook_with_flake8_tags.ipynb")


def get_test_intermediate_path(intermediate_names):
    return [
        filename
        for filename in intermediate_names
        if filename.endswith("notebook_with_flake8_tags.ipynb_parsed")
    ][0]


def get_mocked_option(notebook_cell_format: str, formatter="default_notebook") -> Values:
    return Values(
        {"output_file": "", "format": formatter, "notebook_cell_format": notebook_cell_format}
    )


def get_mocked_violation(filename: str, line_number: int) -> Violation:
    return Violation(
        filename=os.path.normpath(filename),
        line_number=line_number,
        physical_line=0,
        column_number=2,
        code="AB123",
        text="This is just for the coverage",
    )


@pytest.mark.parametrize(
    "line_number,cell_nr,expected_line_number",
    [
        (8, 1, 2),
        (15, 2, 2),
        (29, 4, 2),
        (30, 4, 3),
        (38, 5, 3),
    ],
)
@pytest.mark.parametrize(
    "notebook_cell_format,cell_format_str",
    (
        ("{nb_path}#In[{exec_count}]", "#In[{}]"),
        ("{nb_path}:code_cell#{exec_count}", ":code_cell#{}"),
    ),
)
def test_IpynbFormatter__map_notebook_error(
    notebook_parser: NotebookParser,
    notebook_cell_format: str,
    cell_format_str: str,
    line_number: int,
    cell_nr: int,
    expected_line_number: int,
):
    expected_filename = f"{TEST_NOTEBOOK_PATH}{cell_format_str.format(cell_nr)}"
    filename = get_test_intermediate_path(notebook_parser.intermediate_py_file_paths)
    mock_error = get_mocked_violation(filename, line_number)
    map_result = map_notebook_error(mock_error, notebook_cell_format)
    assert map_result is not None
    filename, input_cell_line_number = map_result
    assert input_cell_line_number == expected_line_number
    assert filename == expected_filename


@pytest.mark.parametrize(
    "format_str,file_path_list,expected_result_str",
    [
        (
            "default_notebook",
            [],
            "{expected_filename}:2:2: AB123 This is just for the coverage",
        ),
        (
            "%(path)s:%(row)d: %(text)s",
            [],
            "{expected_filename}:2: This is just for the coverage",
        ),
        (
            "default_notebook",
            ["tests", "data", "notebooks", "falsy_python_file.py"],
            "{expected_filename}:8:2: AB123 This is just for the coverage",
        ),
        (
            "default_notebook",
            [
                "tests",
                "data",
                "intermediate_py_files",
                "notebook_with_flake8_tags.ipynb_parsed",
            ],
            "{expected_filename}:8:2: AB123 This is just for the coverage",
        ),
    ],
)
@pytest.mark.parametrize(
    "notebook_cell_format,cell_format_str",
    (
        ("{nb_path}#In[{exec_count}]", "#In[1]"),
        ("{nb_path}:code_cell#{exec_count}", ":code_cell#1"),
    ),
)
def test_IpynbFormatter__format(
    notebook_cell_format: str,
    cell_format_str: str,
    notebook_parser: NotebookParser,
    file_path_list: List[str],
    format_str: str,
    expected_result_str: str,
):
    mocked_option = get_mocked_option(notebook_cell_format, format_str)
    formatter = IpynbFormatter(mocked_option)  # type: ignore
    if file_path_list:
        filename = expected_filename = os.path.join(*file_path_list)
    else:
        expected_filename = f"{TEST_NOTEBOOK_PATH}{cell_format_str}"
        filename = get_test_intermediate_path(notebook_parser.intermediate_py_file_paths)
    mock_error = get_mocked_violation(filename, 8)
    result = formatter.format(mock_error)
    expected_result = expected_result_str.format(expected_filename=expected_filename)
    assert result == expected_result
