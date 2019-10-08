import json
import os

# import tempfile
from typing import Dict, List, Tuple

import warnings

from nbconvert.filters import ipython2python

from .cell_parsers import notebook_cell_to_intermediate_py_str


def ignore_cell(notebook_cell: Dict):
    if not notebook_cell["source"]:
        return True
    elif notebook_cell["cell_type"] != "code":
        return True
    else:
        return False


class InvalidNotebookWarning(UserWarning):
    pass


def warn_invalid_notebook(notebook_path: str):
    warnings.warn(
        f"Error parsing notebook at path '{notebook_path}'. "
        "Make sure this is a valid notebook.",
        InvalidNotebookWarning,
    )


def read_notebook_to_cells(notebook_path: str) -> List[Dict]:
    try:
        with open(notebook_path) as notebook_file:
            notebook_cells = json.load(notebook_file)["cells"]
            return notebook_cells
    except json.JSONDecodeError:
        warn_invalid_notebook(notebook_path)
        return []


def get_notebook_code_cells(notebook_path: str) -> Tuple[bool, List[str]]:
    uses_get_ipython = False
    notebook_cells = read_notebook_to_cells(notebook_path)
    for index, cell in list(enumerate(notebook_cells))[::-1]:
        if ignore_cell(cell):
            notebook_cells.pop(index)
        else:
            cell_source = list(enumerate(cell["source"]))[::-1]
            for source_index, source_line in cell_source:
                new_source_line = ipython2python(source_line)
                if new_source_line.startswith("get_ipython"):
                    uses_get_ipython = True
                cell["source"][source_index] = new_source_line

    return uses_get_ipython, notebook_cells


def create_temp_path(notebook_path: str, temp_base_path: str):
    abs_notebook_path = os.path.abspath(notebook_path)
    if abs_notebook_path.startswith(os.path.abspath(os.curdir)):
        rel_file_path = os.path.relpath(notebook_path, os.curdir)
        temp_file_path = os.path.abspath(os.path.join(temp_base_path, rel_file_path))
    else:
        temp_file_path = os.path.join(temp_base_path, os.path.split(notebook_path)[1])
    temp_file_path = f"{os.path.splitext(temp_file_path)[0]}.py"
    temp_dir_path = os.path.dirname(temp_file_path)
    if not os.path.isdir(temp_dir_path):
        os.makedirs(temp_dir_path)
    return temp_file_path


def create_intermediate_py_file(notebook_path: str, intermediate_dir_base_path: str):
    intermediate_file_path = create_temp_path(notebook_path, intermediate_dir_base_path)
    uses_get_ipython, notebook_cells = get_notebook_code_cells(notebook_path)
    intermediate_py_str_list = []
    for notebook_cell in notebook_cells:
        intermediate_py_str_list.append(
            notebook_cell_to_intermediate_py_str(notebook_cell)
        )
    if uses_get_ipython:
        intermediate_code = "from IPython import get_ipython\n\n\n"
    else:
        intermediate_code = ""

    intermediate_code += "".join(intermediate_py_str_list)
    with open(intermediate_file_path, "w+") as intermediate_file:
        intermediate_file.write(intermediate_code)
    return intermediate_file_path
