# -*- coding: utf-8 -*-

"""Module for parsing whole jupyter notebooks.
This utilizes ``flake8_nb.parser.cell_parsers``."""

import json
import os
import warnings
from typing import Dict, Iterator, List, Tuple

from nbconvert.filters import ipython2python

from .cell_parsers import notebook_cell_to_intermediate_dict


def ignore_cell(notebook_cell: Dict) -> bool:
    """
    Return True if the cell isn't a code cell or is empty.

    Parameters
    ----------
    notebook_cell : Dict
        Dict representation of a notebook cell as parsed from JSON.

    Returns
    -------
    bool
        Whether cell should be ignored or not.
    """
    if not notebook_cell["source"]:
        return True
    elif notebook_cell["cell_type"] != "code":
        return True
    else:
        return False


class InvalidNotebookWarning(UserWarning):
    """
    Warning that is given when a jupyter notebook can't be parsed as JSON.
    """

    def __init__(self, notebook_path, *args, **kwargs):
        super().__init__(
            f"Error parsing notebook at path '{notebook_path}'. "
            "Make sure this is a valid notebook."
        )


def read_notebook_to_cells(notebook_path: str) -> List[Dict]:
    r"""
    Parses the notebook at ``notebook_path`` as Json and returns a list of notebook
    cells.

    Parameters
    ----------
    notebook_path : str
        Path to a notebook.

    Returns
    -------
    List[Dict]
        List of notebook cells if the notebook was parsed successfully or
        an empty list if the \*.ipynb file couldn't be parsed.

    Warns
    -----
    InvalidNotebookWarning
        If the notebook couldn't be parsed.
    """
    try:
        with open(notebook_path) as notebook_file:
            notebook_cells = json.load(notebook_file)["cells"]
            return notebook_cells
    except (json.JSONDecodeError, KeyError):
        warnings.warn(InvalidNotebookWarning(notebook_path))
        return []


def convert_source_line(source_line: str) -> str:
    """
    Transforms jupyter magic commands to valid python code,
    utilizing ``nbconvert.filters.ipython2python``.

    Parameters
    ----------
    source_line : str
        Single line of source code.

    Returns
    -------
    str
        Valid python code, as string, even if it was a
        jupyter magic line.
    """
    if source_line.startswith(("!", "?", "%")) or source_line.endswith(("?")):
        return ipython2python(source_line)
    else:
        return source_line


def get_notebook_code_cells(notebook_path: str) -> Tuple[bool, List[Dict]]:
    """
    Parses a notebook and returns a Tuple, with the first entry
    beeing a bool which indedicates if juypter magic way used and
    the second entry is a List of all code cells, as their dict
    representation.

    Parameters
    ----------
    notebook_path : str
        Path to a notebook.

    Returns
    -------
    Tuple[bool, List[Dict]]
        (``uses_get_ipython``, ``notebook_cells``), where ``uses_get_ipython``
        is a bool, which is ``True`` if any cell contained jupyter magic and
        ``notebook_cells`` is a List of all code cells dict representation.

    See Also
    --------
    read_notebook_to_cells

    Warns
    -----
    InvalidNotebookWarning
        If the notebook couldn't be parsed.
    """
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
        This function uses `os.path.normcase` to prevent conflicts
        in Windows path names.
    """
    path = os.path.normcase(os.path.abspath(path))
    parent_dir = os.path.normcase(os.path.abspath(parent_dir))
    if path.startswith(parent_dir):
        return True
    else:
        return False


def create_temp_path(notebook_path: str, temp_base_path: str) -> str:
    """
    Creates the path for a parsed jupyter notebook, which has
    the same relative position to ``temp_base_path`` as
    ``notebook_path`` has to ``os.curdir``. If that would lead out
    of the ``temp_base_path``, the path will point to a file
    at the root of ``temp_base_path``, which has the same filename
    as the file at ``notebook_path`` has.

    Parameters
    ----------
    notebook_path : str
        Path to a notebook.
    temp_base_path : str
        Base path of a temporary folder, the new path should have the
        same relative position to as ``notebook_path`` has to ``os.curdir``

    Returns
    -------
    str
        Path to the temporary file which should be created.
    """
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
    r"""
    Parses a notebook at ``notebook_path`` and saves a parsed
    version to the corresponding position relative to
    ``intermediate_dir_base_path``.

    Parameters
    ----------
    notebook_path : str
        Path to a notebook.
    intermediate_dir_base_path : str
        Path pointing to the position the parsed notebook
        will be saved to.

    Returns
    -------
    Tuple[str, Dict]
        (``intermediate_file_path``, ``input_line_mapping``) Where
        ``intermediate_file_path`` is the path the parsed notebook
        was written to. If there was an error parsing the file
        the ``intermediate_file_path`` will be ``""``.
        ``input_line_mapping`` is a dict which has the keys
        'input_names' and 'code_lines'. ``code_lines`` is a List
        of the code cells ``In[\d\*]`` names and ``code_lines``
        is the corresponding line in the parsed notebook.

    See Also
    --------
    read_notebook_to_cells, get_notebook_code_cells, create_temp_path

    Warns
    -----
    InvalidNotebookWarning
        If the notebook couldn't be parsed.
    """
    intermediate_file_path = create_temp_path(notebook_path, intermediate_dir_base_path)
    uses_get_ipython, notebook_cells = get_notebook_code_cells(notebook_path)
    input_line_mapping: Dict[str, List] = {"input_names": [], "code_lines": []}
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
    """
    rel_paths = []
    for file_path in file_paths:
        rel_path = os.path.normpath(os.path.relpath(file_path, base_path))
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
    """
    Main parsing class for notebooks.
    ``NotebookParser`` utilizes that instance and class attributes
    are seperated and class attributes allow sharing of information
    across instances. This is used to realize the mapping of checked
    parsed notebooks back to their original files.

    """

    original_notebook_paths: List[str] = []
    """List of paths to the original Notebooks"""
    intermediate_py_file_paths: List[str] = []
    """List of paths to the parsed Notebooks"""
    input_line_mappings: List[Dict[str, List]] = []
    """List of input_line_mapping"""
    temp_path = ""
    """Path of the temp folder the parsed notebooks were saved in"""

    def __init__(self, original_notebook_paths: List[str] = None):
        """
        Initializing an instace of the class will save ``original_notebook_paths``,
        which is a List of paths to notebooks, to the class attributes, which can be
        accessed by all instaces or all modules that know about the class.
        If ``original_notebook_paths`` isn't provided, the class attributes will stay
        as it was.

        Parameters
        ----------
        original_notebook_paths : List[str], optional
            List of paths to notebooks, by default None
        """
        self.new_notebooks = False

        if original_notebook_paths:
            self.new_notebooks = True
            NotebookParser.original_notebook_paths = original_notebook_paths
        self.create_intermediate_py_file_paths()
        # This is needed
        NotebookParser.intermediate_py_file_paths.reverse()
        NotebookParser.input_line_mappings.reverse()

    def create_intermediate_py_file_paths(self):
        """
        Parses all notebooks provided by ``self.original_notebook_paths``
        and saves them to a temporary directory, if ``original_notebook_paths``,
        was provided at initialization.

        """
        if self.original_notebook_paths and self.new_notebooks:
            import tempfile

            NotebookParser.input_line_mappings = []
            NotebookParser.intermediate_py_file_paths = []

            NotebookParser.temp_path = tempfile.mkdtemp(prefix="flake8_nb_")
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
    def get_mappings() -> Iterator[Tuple[str, str, Dict]]:
        """
        Return the mapping information needed to generate error messages
        corresponding to the original notebook and not the actually checked
        parsed one.

        Returns
        -------
        Iterator[Tuple[str, str, Dict]]
            (``original_notebook_paths``,
            ``intermediate_py_file_paths``,
            ``input_line_mappings``)
            ``original_notebook_paths`` is the relative path of the tested notebook.
            ``intermediate_py_file_paths`` is the absolute path of the checked notebook.
            And ``input_line_mapping`` is a dict of information about which input in
            the original notebook, is in what line in the corresponding pared notebook.

        See Also
        --------
        input_line_mapping, create_intermediate_py_file
        """
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
        """
        Deletes the created temporary directory if it exists and
        resets all class attributes.
        """
        import shutil

        if NotebookParser.temp_path:
            shutil.rmtree(NotebookParser.temp_path, ignore_errors=True)

        NotebookParser.original_notebook_paths = []
        NotebookParser.intermediate_py_file_paths = []
        NotebookParser.input_line_mappings = []
        NotebookParser.temp_path = ""
