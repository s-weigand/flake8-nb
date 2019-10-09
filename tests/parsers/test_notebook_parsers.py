import os
from typing import Dict, List, Tuple

import pytest

from flake8_nb.parsers.notebook_parsers import (
    create_intermediate_py_file,
    create_temp_path,
    get_notebook_code_cells,
    ignore_cell,
    InvalidNotebookWarning,
    read_notebook_to_cells,
    warn_invalid_notebook,
)

TEST_NOTEBOOK_BASE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data", "test_notebooks")
)

INTERMEDIATE_PY_FILE_BASE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data", "intermediate_py_files")
)


def get_expected_intermediate_file_results(
    result_name: str, base_path: str
) -> Tuple[str, str]:
    expected_result_path = os.path.join(
        base_path, "tests", "data", "test_notebooks", result_name
    )
    expected_result_file_path = os.path.join(
        INTERMEDIATE_PY_FILE_BASE_PATH, result_name
    )
    with open(expected_result_file_path) as result_file:
        expected_result_str = result_file.read()
    return expected_result_path, expected_result_str


@pytest.mark.parametrize(
    "notebook_name",
    [
        "not_a_notebook",
        "notebook_with_flake8_tags",
        "notebook_with_out_flake8_tags",
        "notebook_with_ipython_magic",
    ],
)
def test_create_intermediate_py_file(tmpdir, notebook_name: str):
    notebook_path = os.path.join(TEST_NOTEBOOK_BASE_PATH, f"{notebook_name}.ipynb")

    tmp_base_path = str(tmpdir)
    expected_result_path, expected_result_str = get_expected_intermediate_file_results(
        f"{notebook_name}.py", tmp_base_path
    )
    if notebook_name.startswith("not_a_notebook"):
        with pytest.warns(InvalidNotebookWarning):
            intermediate_file_path = create_intermediate_py_file(
                notebook_path, tmp_base_path
            )
            assert intermediate_file_path == expected_result_path
            with open(intermediate_file_path) as result_file:
                assert result_file.read() == expected_result_str
    else:
        intermediate_file_path = create_intermediate_py_file(
            notebook_path, tmp_base_path
        )
        assert intermediate_file_path == expected_result_path
        with open(intermediate_file_path) as result_file:
            assert result_file.read() == expected_result_str


@pytest.mark.parametrize(
    "notebook_path,rel_result_path",
    [
        (os.path.join(os.curdir, "file_name.ipynb"), ["file_name.py"]),
        (os.path.join(os.curdir, "../file_name.ipynb"), ["file_name.py"]),
        (
            os.path.join(os.curdir, "sub_dir", "file_name.ipynb"),
            ["sub_dir", "file_name.py"],
        ),
        (
            os.path.join(os.curdir, "sub_dir", "sub_sub_dir", "file_name.ipynb"),
            ["sub_dir", "sub_sub_dir", "file_name.py"],
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
        ("notebook_with_flake8_tags.ipynb", 6, False),
        ("notebook_with_out_flake8_tags.ipynb", 2, False),
        ("notebook_with_ipython_magic.ipynb", 1, True),
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
    "notebook_name,number_of_cells",
    [
        ("not_a_notebook.ipynb", 0),
        ("notebook_with_flake8_tags.ipynb", 16),
        ("notebook_with_out_flake8_tags.ipynb", 7),
        ("notebook_with_ipython_magic.ipynb", 3),
    ],
)
def test_read_notebook_to_cells(notebook_name: str, number_of_cells: int):
    notebook_path = os.path.join(TEST_NOTEBOOK_BASE_PATH, notebook_name)
    if notebook_name.startswith("not_a_notebook"):
        with pytest.warns(InvalidNotebookWarning):
            assert len(read_notebook_to_cells(notebook_path)) == number_of_cells
    else:
        assert len(read_notebook_to_cells(notebook_path)) == number_of_cells


def test_warn_invalid_notebook():
    with pytest.warns(
        InvalidNotebookWarning,
        match=(
            "Error parsing notebook at path 'invalid_notebook.ipynb'. "
            "Make sure this is a valid notebook."
        ),
    ):
        warn_invalid_notebook("invalid_notebook.ipynb")
