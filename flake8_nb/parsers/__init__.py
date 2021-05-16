"""Package responsible for transforming notebooks to valid python files."""
from typing import Any
from typing import Dict
from typing import NamedTuple

NotebookCell = Dict[str, Any]


class CellId(NamedTuple):
    """Container to hold information to identify a cell.

    The information are:
    * ``input_nr``
        Execution count, " " for not executed cells
    * ``code_cell_nr``
        Count of the code cell starting at 1, ignoring raw and markdown cells
    * ``total_cell_nr``
        Total count of the cell starting at 1, considering raw and markdown cells.
    """

    input_nr: str
    code_cell_nr: int
    total_cell_nr: int
