import os
import warnings
from typing import Dict
from typing import List
from typing import Tuple
from typing import Union

import pytest

from flake8_nb.parsers import CellId
from flake8_nb.parsers.notebook_parsers import InputLineMapping
from flake8_nb.parsers.notebook_parsers import InvalidNotebookWarning
from flake8_nb.parsers.notebook_parsers import NotebookParser
from flake8_nb.parsers.notebook_parsers import create_intermediate_py_file
from flake8_nb.parsers.notebook_parsers import create_temp_path
from flake8_nb.parsers.notebook_parsers import get_notebook_code_cells
from flake8_nb.parsers.notebook_parsers import get_rel_paths
from flake8_nb.parsers.notebook_parsers import ignore_cell
from flake8_nb.parsers.notebook_parsers import is_parent_dir
from flake8_nb.parsers.notebook_parsers import map_intermediate_to_input
from flake8_nb.parsers.notebook_parsers import read_notebook_to_cells
from tests import TEST_NOTEBOOK_BASE_PATH

INTERMEDIATE_PY_FILE_BASE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data", "intermediate_py_files")
)


def get_expected_intermediate_file_results(result_name: str, base_path: str) -> Tuple[str, str]:
    expected_result_path = os.path.join(base_path, "tests", "data", "notebooks", result_name)
    expected_result_file_path = os.path.join(INTERMEDIATE_PY_FILE_BASE_PATH, result_name)
    if result_name.startswith("not_a_notebook"):
        expected_result_str = ""
    else:
        with open(expected_result_file_path) as result_file:
            expected_result_str = result_file.read()
    return expected_result_path, expected_result_str


@pytest.mark.parametrize(
    "notebook_name,expected_input_line_mapping",
    [
        ("not_a_notebook", {"input_ids": [], "code_lines": []}),
        (
            "notebook_with_flake8_tags",
            {
                "input_ids": [
                    CellId("1", 1, 4),
                    CellId("2", 2, 6),
                    CellId("3", 3, 8),
                    CellId("4", 4, 11),
                    CellId("5", 5, 13),
                    CellId("6", 6, 15),
                    CellId("7", 7, 18),
                    CellId("8", 8, 20),
                    CellId("9", 9, 22),
                    CellId("10", 10, 24),
                ],
                "code_lines": [4, 11, 18, 25, 33, 41, 49, 56, 62, 68],
            },
        ),
        (
            "notebook_with_out_ipython_magic",
            {"input_ids": [CellId("1", 1, 3)], "code_lines": [1]},
        ),
        (
            "cell_with_source_string",
            {"input_ids": [("1", 1, 1)], "code_lines": [1]},
        ),
        (
            "notebook_with_out_flake8_tags",
            {
                "input_ids": [
                    CellId("1", 1, 3),
                    CellId("2", 2, 5),
                    CellId("3", 3, 7),
                    CellId("4", 4, 9),
                    CellId("5", 6, 13),
                    CellId("6", 7, 15),
                    CellId("7", 8, 17),
                    CellId("8", 9, 19),
                ],
                "code_lines": [4, 10, 16, 23, 31, 37, 43, 49],
            },
        ),
    ],
)
def test_create_intermediate_py_file(
    tmpdir, notebook_name: str, expected_input_line_mapping: Dict[str, List[Union[str, int]]]
):
    notebook_path = os.path.join(TEST_NOTEBOOK_BASE_PATH, f"{notebook_name}.ipynb")

    tmp_base_path = str(tmpdir)
    expected_result_path, expected_result_str = get_expected_intermediate_file_results(
        f"{notebook_name}.ipynb_parsed", tmp_base_path
    )
    if notebook_name.startswith("not_a_notebook"):
        with pytest.warns(InvalidNotebookWarning):
            intermediate_file_path, input_line_mapping = create_intermediate_py_file(
                notebook_path, tmp_base_path
            )
            assert intermediate_file_path == ""
            assert input_line_mapping == expected_input_line_mapping
    else:
        intermediate_file_path, input_line_mapping = create_intermediate_py_file(
            notebook_path, tmp_base_path
        )
        assert intermediate_file_path == expected_result_path
        assert input_line_mapping == expected_input_line_mapping
        with open(intermediate_file_path) as result_file:
            assert result_file.read() == expected_result_str


@pytest.mark.parametrize(
    "notebook_path,rel_result_path",
    [
        (os.path.join(os.curdir, "file_name.ipynb"), ["file_name.ipynb_parsed"]),
        (os.path.join(os.curdir, "../file_name.ipynb"), ["file_name.ipynb_parsed"]),
        (
            os.path.join(os.curdir, "sub_dir", "file_name.ipynb"),
            ["sub_dir", "file_name.ipynb_parsed"],
        ),
        (
            os.path.join(os.curdir, "sub_dir", "sub_sub_dir", "file_name.ipynb"),
            ["sub_dir", "sub_sub_dir", "file_name.ipynb_parsed"],
        ),
    ],
)
def test_create_temp_path(tmpdir, notebook_path: str, rel_result_path: List[str]):
    expected_result_path = os.path.join(str(tmpdir), *rel_result_path)
    result_path = create_temp_path(notebook_path, str(tmpdir))
    assert result_path == os.path.abspath(expected_result_path)
    assert os.path.isdir(os.path.dirname(result_path))


@pytest.mark.parametrize(
    "notebook_name,number_of_cells,uses_get_ipython_result",
    [
        ("not_a_notebook.ipynb", 0, False),
        ("cell_with_source_string.ipynb", 1, False),
        ("notebook_with_flake8_tags.ipynb", 10, True),
        ("notebook_with_out_flake8_tags.ipynb", 8, True),
        ("notebook_with_out_ipython_magic.ipynb", 1, False),
    ],
)
def test_get_notebook_code_cells(
    notebook_name: str, number_of_cells: int, uses_get_ipython_result: bool
):
    notebook_path = os.path.join(TEST_NOTEBOOK_BASE_PATH, notebook_name)
    if notebook_name.startswith("not_a_notebook"):
        with pytest.warns(InvalidNotebookWarning):
            uses_get_ipython, notebook_cells = get_notebook_code_cells(notebook_path)
            assert uses_get_ipython == uses_get_ipython_result
            assert len(notebook_cells) == number_of_cells
    else:
        uses_get_ipython, notebook_cells = get_notebook_code_cells(notebook_path)
        assert uses_get_ipython == uses_get_ipython_result
        assert len(notebook_cells) == number_of_cells


@pytest.mark.parametrize(
    "file_paths,base_path,expected_result",
    [
        (
            [os.curdir, os.path.join(os.curdir, "file.foo")],
            os.curdir,
            [".", "file.foo"],
        ),
        (
            [os.path.join(os.curdir, "..", "file.foo")],
            os.curdir,
            [f"..{os.sep}file.foo"],
        ),
    ],
)
def test_get_rel_paths(file_paths: List[str], base_path: str, expected_result: List[str]):
    assert get_rel_paths(file_paths, base_path) == expected_result


@pytest.mark.parametrize(
    "notebook_cell,expected_result",
    [
        ({"source": ["print('foo')"], "cell_type": "code"}, False),
        ({"source": ["## print('foo')"], "cell_type": "markdown"}, True),
        ({"source": [], "cell_type": "code"}, True),
    ],
)
def test_ignore_cell(notebook_cell: Dict, expected_result: bool):
    assert ignore_cell(notebook_cell) == expected_result


@pytest.mark.parametrize(
    "parent_dir,path,expected_result",
    [
        (os.curdir, os.curdir, True),
        (os.curdir, os.path.join(os.curdir, "file.foo"), True),
        (os.curdir, os.path.join(os.curdir, "subdir", "file.foo"), True),
        (os.curdir, os.path.join(os.curdir, "..", "file.foo"), False),
    ],
)
def test_is_parent_dir(parent_dir: str, path: str, expected_result):
    assert is_parent_dir(parent_dir, path) == expected_result


@pytest.mark.parametrize(
    "notebook_name,number_of_cells",
    [
        ("not_a_notebook.ipynb", 0),
        ("notebook_with_flake8_tags.ipynb", 24),
        ("notebook_with_out_flake8_tags.ipynb", 19),
        ("notebook_with_out_ipython_magic.ipynb", 3),
    ],
)
def test_read_notebook_to_cells(notebook_name: str, number_of_cells: int):
    notebook_path = os.path.join(TEST_NOTEBOOK_BASE_PATH, notebook_name)
    if notebook_name.startswith("not_a_notebook"):
        with pytest.warns(InvalidNotebookWarning):
            assert len(read_notebook_to_cells(notebook_path)) == number_of_cells
    else:
        assert len(read_notebook_to_cells(notebook_path)) == number_of_cells


def test_InvalidNotebookWarning():
    with pytest.warns(
        InvalidNotebookWarning,
        match=(
            "Error parsing notebook at path 'dummy_path'. " "Make sure this is a valid notebook."
        ),
    ):
        warnings.warn(InvalidNotebookWarning("dummy_path"))


@pytest.mark.parametrize(
    "line_number,expected_result",
    [(15, (("2", 2, 2), 2)), (30, (("4", 4, 5), 3)), (52, (("7", 9, 15), 1))],
)
def test_map_intermediate_to_input_line(line_number: int, expected_result: Tuple[str, int]):
    input_line_mapping: InputLineMapping = {
        "input_ids": [
            CellId("1", 1, 1),
            CellId("2", 2, 2),
            CellId("3", 3, 3),
            CellId("4", 4, 5),
            CellId("5", 6, 8),
            CellId("6", 7, 10),
            CellId("7", 9, 15),
        ],
        "code_lines": [4, 11, 18, 25, 33, 41, 49],
    }
    assert map_intermediate_to_input(input_line_mapping, line_number) == expected_result


#################################
#     NotebookParser Tests      #
#################################


def test_NotebookParser_create_intermediate_py_file_paths(
    notebook_parser: NotebookParser,
):
    for original_notebook in notebook_parser.original_notebook_paths:
        assert os.path.isfile(original_notebook)
    for intermediate_py_file in notebook_parser.intermediate_py_file_paths:
        assert os.path.isfile(intermediate_py_file)
    assert notebook_parser.temp_path != ""

    original_count = len(notebook_parser.original_notebook_paths)
    intermediate_count = len(notebook_parser.intermediate_py_file_paths)
    input_line_mapping_count = len(notebook_parser.input_line_mappings)
    assert original_count == 3
    assert intermediate_count == 3
    assert input_line_mapping_count == 3


def test_NotebookParser_cross_instance_value_propagation(
    notebook_parser: NotebookParser,
):
    notebook_parser.get_mappings()
    new_parser_instance = NotebookParser()

    original_count = len(new_parser_instance.original_notebook_paths)
    intermediate_count = len(new_parser_instance.intermediate_py_file_paths)
    input_line_mapping_count = len(new_parser_instance.input_line_mappings)
    assert original_count == 3
    assert intermediate_count == 3
    assert input_line_mapping_count == 3


def test_NotebookParser_clean_up(notebook_parser: NotebookParser):
    temp_path = notebook_parser.temp_path
    notebook_parser.clean_up()
    assert not os.path.exists(temp_path)
    assert notebook_parser.temp_path == ""

    original_count = len(notebook_parser.original_notebook_paths)
    intermediate_count = len(notebook_parser.intermediate_py_file_paths)
    input_line_mapping_count = len(notebook_parser.input_line_mappings)
    assert original_count == 0
    assert intermediate_count == 0
    assert input_line_mapping_count == 0
