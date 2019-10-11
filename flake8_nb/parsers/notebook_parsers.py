import json
import os
from typing import Dict, Iterator, List, Tuple
import warnings

from nbconvert.filters import ipython2python


from .cell_parsers import notebook_cell_to_intermediate_dict


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


def convert_source_line(source_line: str):
    if source_line.startswith(("!", "?", "%")):
        return ipython2python(source_line)
    else:
        return source_line


def get_notebook_code_cells(notebook_path: str) -> Tuple[bool, List[str]]:
    uses_get_ipython = False
    notebook_cells = read_notebook_to_cells(notebook_path)
    for index, cell in list(enumerate(notebook_cells))[::-1]:
        if ignore_cell(cell):
            notebook_cells.pop(index)
        else:
            cell_source = list(enumerate(cell["source"]))[::-1]
            for source_index, source_line in cell_source:
                new_source_line = convert_source_line(source_line)
                if new_source_line.startswith("get_ipython"):
                    uses_get_ipython = True
                cell["source"][source_index] = new_source_line

    return uses_get_ipython, notebook_cells


def is_parent_dir(parent_dir: str, path: str) -> bool:
    """
    Checks if a given dir `parent_dir` is parent directory of `path`.

    Parameters
    ----------
    parent_dir : str
        Path to the directory, which should be checked if it is a
        parent directory of `path`.
    path : str
        Path to a file or directory, which should be checked if
        it is inside of `parent_dir`..

    Returns
    -------
    bool
        Weather or not 'path' is inside of 'parent_dir'.

    Notes
    -----
    This function uses `os.path.normcase` to prevent conflicts in windows path names.
    """
    path = os.path.normcase(os.path.abspath(path))
    parent_dir = os.path.normcase(os.path.abspath(parent_dir))
    if path.startswith(parent_dir):
        return True
    else:
        return False


def create_temp_path(notebook_path: str, temp_base_path: str):
    abs_notebook_path = os.path.abspath(notebook_path)
    if is_parent_dir(os.curdir, abs_notebook_path):
        rel_file_path = os.path.relpath(abs_notebook_path, os.curdir)
        temp_file_path = os.path.abspath(os.path.join(temp_base_path, rel_file_path))
    else:
        temp_file_path = os.path.join(temp_base_path, os.path.split(notebook_path)[1])
    temp_file_path = f"{os.path.splitext(temp_file_path)[0]}.ipynb_parsed"
    temp_dir_path = os.path.dirname(temp_file_path)
    if not os.path.isdir(temp_dir_path):
        os.makedirs(temp_dir_path)
    return temp_file_path


def create_intermediate_py_file(
    notebook_path: str, intermediate_dir_base_path: str
) -> Tuple[str, Dict]:
    intermediate_file_path = create_temp_path(notebook_path, intermediate_dir_base_path)
    uses_get_ipython, notebook_cells = get_notebook_code_cells(notebook_path)
    input_line_mapping = {"input_names": [], "code_lines": []}
    if uses_get_ipython:
        lines_of_code = 3
        intermediate_code = "from IPython import get_ipython\n\n\n"
    else:
        lines_of_code = 0
        intermediate_code = ""
    intermediate_py_str_list = []
    for notebook_cell in notebook_cells:
        intermediate_dict = notebook_cell_to_intermediate_dict(notebook_cell)
        intermediate_py_str_list.append(intermediate_dict["code"])
        input_line_mapping["input_names"].append(intermediate_dict["input_name"])
        input_line_mapping["code_lines"].append(lines_of_code + 1)
        lines_of_code += intermediate_dict["lines_of_code"]

    intermediate_code += "".join(intermediate_py_str_list).rstrip("\n")
    if intermediate_code:
        with open(intermediate_file_path, "w+") as intermediate_file:
            intermediate_file.write(f"{intermediate_code}\n")
        return intermediate_file_path, input_line_mapping
    else:
        return "", input_line_mapping


def get_rel_paths(file_paths: List[str], base_path: str) -> List[str]:
    """
    Transforms `file_paths` in a list of paths relative to `base_path`.

    Parameters
    ----------
    file_paths : List[str]
        List of file paths.
    base_path : str
        Path `file_paths` should be relative to.

    Returns
    -------
    List[str]
        List of `file_paths` relative to `base_path`

    Notes
    -----
    Windows paths will be seperated by '/' instead of '\\'.
    """
    rel_paths = []
    for file_path in file_paths:
        rel_path = os.path.normpath(os.path.relpath(file_path, base_path))
        if os.path.altsep:
            rel_path = rel_path.replace(os.path.sep, os.path.altsep)
        rel_paths.append(rel_path)
    return rel_paths


def map_intermediate_to_input(
    input_line_mapping: Dict[str, List], line_number: int
) -> Tuple[str, int]:
    """
    Remaps the line at `line_number` to the corresponding code cell
    (`input_cell_name`) and line number in the code cell
    (`input_cell_line_number`)

    Parameters
    ----------
    input_line_mapping : Dict[str, List]
        Dict containing lists of input cell names and their line in the
        intermediate file.
    line_number : int
        Line in the intermediate py file.

    Returns
    -------
    Tuple[str, int]
        Input cell name and corresponding line in that cell
        (input_cell_name, input_cell_line_number)

    See Also
    --------
    create_intermediate_py_file
    """
    line_filter = filter(
        lambda code_line: code_line < line_number, input_line_mapping["code_lines"]
    )
    entry_index = len(list(line_filter)) - 1
    input_cell_name = input_line_mapping["input_names"][entry_index]
    code_starting_line_number = input_line_mapping["code_lines"][entry_index] + 2
    input_cell_line_number = code_starting_line_number - line_number
    return input_cell_name, abs(input_cell_line_number)


class NotebookParser:
    original_notebook_paths = []
    intermediate_py_file_paths = []
    input_line_mappings = []
    temp_path = ""

    def __init__(self, original_notebook_paths: List[str] = None):
        self.new_notebooks = False

        if original_notebook_paths:
            self.new_notebooks = True
            NotebookParser.original_notebook_paths = original_notebook_paths
        self.create_intermediate_py_file_paths()

    def create_intermediate_py_file_paths(self):
        if self.original_notebook_paths and self.new_notebooks:
            import tempfile

            NotebookParser.input_line_mappings = []
            NotebookParser.intermediate_py_file_paths = []

            NotebookParser.temp_path = tempfile.mkdtemp()
            index_orig_list = list(enumerate(self.original_notebook_paths))[::-1]
            for index, original_notebook_path in index_orig_list:
                intermediate_py_file_path, input_line_mapping = create_intermediate_py_file(
                    original_notebook_path, self.temp_path
                )
                if intermediate_py_file_path:
                    NotebookParser.intermediate_py_file_paths.append(
                        intermediate_py_file_path
                    )
                    NotebookParser.input_line_mappings.append(input_line_mapping)
                else:
                    NotebookParser.original_notebook_paths.pop(index)

    @staticmethod
    def get_mappings() -> Iterator[Tuple[str, str]]:
        rel_original_notebook_paths = get_rel_paths(
            NotebookParser.original_notebook_paths, os.curdir
        )
        return zip(
            rel_original_notebook_paths,
            NotebookParser.intermediate_py_file_paths,
            NotebookParser.input_line_mappings,
        )

    @staticmethod
    def clean_up():
        import shutil

        if NotebookParser.temp_path:
            shutil.rmtree(NotebookParser.temp_path, ignore_errors=True)

        NotebookParser.original_notebook_paths = []
        NotebookParser.intermediate_py_file_paths = []
        NotebookParser.input_line_mappings = []
        NotebookParser.temp_path = ""
