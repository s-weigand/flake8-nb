import json
from typing import Dict


from nbconvert.filters import ipython2python


def ignore_cell(notebook_cell: Dict):
    if not notebook_cell["source"]:
        return True
    elif notebook_cell["cell_type"] != "code":
        return True
    else:
        return False


def get_clean_notebook(notebook_path: str):
    with open(notebook_path) as notebook_file:
        notebook_cells = json.load(notebook_file)["cells"]
    for index, cell in list(enumerate(notebook_cells))[::-1]:
        if ignore_cell(cell):
            notebook_cells.pop(index)
        else:
            cell_source = list(enumerate(cell["source"]))[::-1]
            for source_index, source_line in cell_source:
                cell["source"][source_index] = ipython2python(source_line)
    return notebook_cells
