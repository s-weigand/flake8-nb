import pytest

from typing import Dict

from flake8_nb.parsers.notebook_parsers import ignore_cell


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
