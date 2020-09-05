import warnings
from typing import Dict
from typing import List

import pytest

from flake8_nb.parsers.cell_parsers import InvalidFlake8TagWarning
from flake8_nb.parsers.cell_parsers import extract_flake8_inline_tags
from flake8_nb.parsers.cell_parsers import extract_flake8_tags
from flake8_nb.parsers.cell_parsers import extract_inline_flake8_noqa
from flake8_nb.parsers.cell_parsers import flake8_tag_to_rules_dict
from flake8_nb.parsers.cell_parsers import generate_rules_list
from flake8_nb.parsers.cell_parsers import get_flake8_rules_dict
from flake8_nb.parsers.cell_parsers import notebook_cell_to_intermediate_dict
from flake8_nb.parsers.cell_parsers import update_inline_flake8_noqa
from flake8_nb.parsers.cell_parsers import update_rules_dict


@pytest.mark.parametrize(
    "source_index,rules_dict,expected_result",
    [
        (
            0,
            {"cell": ["noqa"], "1": ["E402", "F401", "W391"]},
            ["E402", "F401", "W391", "noqa"],
        ),
        (1, {"cell": ["noqa"], "1": ["E402", "F401", "W391"]}, ["noqa"]),
        (1, {"1": ["E402", "F401", "W391"]}, []),
    ],
)
def test_generate_rules_list(
    source_index: int, rules_dict: Dict[str, List], expected_result: List
):
    assert sorted(generate_rules_list(source_index, rules_dict)) == expected_result


@pytest.mark.parametrize(
    "notebook_cell,expected_result",
    [
        (
            {
                "execution_count": 8,
                "metadata": {"tags": ["raises-exception", "flake8-noqa-cell-E402-F401"]},
                "source": ["foo  "],
            },
            {"cell": ["E402", "F401"]},
        ),
        (
            {
                "execution_count": 9,
                "metadata": {
                    "tags": [
                        "flake8-noqa-cell-E402-F401",
                        "flake8-noqa-line-1-E402-F401",
                        "flake8-noqa-line-1-W391",
                        "flake8-noqa-cell",
                    ]
                },
                "source": ["foo  # flake8-noqa-line-3-D402         \n "],
            },
            {"cell": ["noqa"], "1": ["W391", "E402", "F401"], "3": ["D402"]},
        ),
        (
            {
                "execution_count": 8,
                "metadata": {"tags": ["raises-exception", "flake8-noqa-cell-E402-F401"]},
                "source": ["foo  # flake8-noqa-cell     ", "bar # flake8-noqa-line-4"],
            },
            {"cell": ["noqa"], "4": ["noqa"]},
        ),
    ],
)
def test_get_flake8_rules_dict(notebook_cell: Dict, expected_result: Dict[str, List]):
    flake8_rules_dict = get_flake8_rules_dict(notebook_cell)
    for key in expected_result:
        assert sorted(flake8_rules_dict[key]) == sorted(expected_result[key])


def test_extract_flake8_tags():
    notebook_cell = {
        "metadata": {
            "tags": [
                "flake8-noqa-cell-E402-F401",
                "flake8-noqa-cell",
                "flake8-noqa-line-1-E402",
                "flake8-noqa-line-1",
                "random-tag",
            ]
        }
    }
    expected_result = [
        "flake8-noqa-cell-E402-F401",
        "flake8-noqa-cell",
        "flake8-noqa-line-1-E402",
        "flake8-noqa-line-1",
    ]
    assert extract_flake8_tags(notebook_cell) == expected_result


def test_extract_flake8_inline_tags():
    notebook_cell = {
        "source": [
            "foo  # flake8-noqa-cell-A402-BC403",
            "foo  # flake8-noqa-cell     ",
            "foo  # flake8-noqa-line-3-D402         \n",
            "foo  # flake8-noqa-line-4",
            "foo  # flake8-noqa-cell-E402 flake8-noqa-cell-F403",
            "foo  # flake8-noqa-line-6-GH402 flake8-noqa-line-6-J403-L43",
            "foo  # noqa    \n",
            '"foo  # flake8-noqa-cell"',
            "foo  # noqa : flake8-noqa-cell some randome stuff",
        ]
    }
    expected_result = [
        "flake8-noqa-cell-A402-BC403",
        "flake8-noqa-cell",
        "flake8-noqa-line-3-D402",
        "flake8-noqa-line-4",
        "flake8-noqa-cell-E402",
        "flake8-noqa-cell-F403",
        "flake8-noqa-line-6-GH402",
        "flake8-noqa-line-6-J403-L43",
    ]
    assert sorted(extract_flake8_inline_tags(notebook_cell)) == sorted(expected_result)


@pytest.mark.parametrize(
    "flake8_noqa_tag,expected_result",
    [
        ("flake8-noqa-cell-E402-F401", {"cell": ["E402", "F401"]}),
        ("flake8-noqa-cell", {"cell": ["noqa"]}),
        ("flake8-noqa-line-1-E402-F401", {"1": ["E402", "F401"]}),
        ("flake8-noqa-line-1", {"1": ["noqa"]}),
        ("flake8-noqa-line-foo-E402-F401", {}),
    ],
)
def test_flake8_tag_to_rules_dict(flake8_noqa_tag: str, expected_result: Dict[str, List]):
    if flake8_noqa_tag == "flake8-noqa-line-foo-E402-F401":
        with pytest.warns(InvalidFlake8TagWarning):
            assert flake8_tag_to_rules_dict(flake8_noqa_tag) == expected_result
    else:
        assert flake8_tag_to_rules_dict(flake8_noqa_tag) == expected_result


@pytest.mark.parametrize(
    "source_index,expected_result",
    [
        ("foo  # noqa: E402, Fasd401", ["E402", "Fasd401"]),
        ("foo  # noqa : E402,      Fasd401 \n", ["E402", "Fasd401"]),
        ("foo  # noqa", ["noqa"]),
        ("foo  # noqa   :  ", ["noqa"]),
        ("foo  # noqa    \n", ["noqa"]),
        ('"foo  # noqa : E402, Fasd401"', []),
        ("foo  # noqa : E402, Fasd401 some randome stuff", []),
        ("get_ipython().run_cell_magic('bash', '', 'echo test')\n", []),
    ],
)
def test_extract_inline_flake8_noqa(source_index: str, expected_result: List):
    assert extract_inline_flake8_noqa(source_index) == expected_result


@pytest.mark.parametrize(
    "notebook_cell,expected_result",
    [
        (
            {
                "execution_count": 8,
                "metadata": {"tags": ["raises-exception", "flake8-noqa-cell-E402-F401"]},
                "source": ["for i in range(1):\n", "    print(i)"],
            },
            {
                "code": "# In[8]\n\n\nfor i in range(1):  # noqa: E402, F401\n    "
                "print(i)  # noqa: E402, F401\n\n\n",
                "input_name": "In[8]",
                "lines_of_code": 7,
            },
        ),
        (
            {
                "execution_count": 9,
                "metadata": {"tags": ["flake8-noqa-line-1-E402-F401", "flake8-noqa-line-1-W391"]},
                "source": ["for i in range(1):\n", "    print(i)"],
            },
            {
                "code": "# In[9]\n\n\nfor i in range(1):  # noqa: E402, F401, W391\n"
                "    print(i)\n\n\n",
                "input_name": "In[9]",
                "lines_of_code": 7,
            },
        ),
        (
            {
                "execution_count": 2,
                "metadata": {"tags": ["flake8-noqa-cell-E402", "flake8-noqa-line-1"]},
                "source": [
                    "for i in range(1):\n",
                    "    print(i)  # noqa:F401, W391",
                    "print('foo')",
                ],
            },
            {
                "code": "# In[2]\n\n\nfor i in range(1):  # noqa: \n"
                "    print(i)  # noqa: E402, F401, W391\n"
                "print('foo')  # noqa: E402\n\n\n",
                "input_name": "In[2]",
                "lines_of_code": 8,
            },
        ),
        (
            {
                "execution_count": 1,
                "metadata": {"tags": ["flake8-noqa-cell", "flake8-noqa-line-1"]},
                "source": ["for i in range(1):\n", "    print(i)  # noqa:F401, W391"],
            },
            {
                "code": "# In[1]\n\n\nfor i in range(1):  # noqa: \n    print(i)  # noqa: \n\n\n",
                "input_name": "In[1]",
                "lines_of_code": 7,
            },
        ),
        (
            {
                "execution_count": None,
                "metadata": {"tags": ["flake8-noqa-cell", "flake8-noqa-line-1"]},
                "source": ["for i in range(1):\n", "    print(i)  # noqa:F401, W391"],
            },
            {
                "code": "# In[ ]\n\n\nfor i in range(1):  # noqa: \n    print(i)  # noqa: \n\n\n",
                "input_name": "In[ ]",
                "lines_of_code": 7,
            },
        ),
    ],
)
def test_notebook_cell_to_intermediate_py_str(
    notebook_cell: Dict, expected_result: Dict[str, str]
):
    intermediate_py_str = notebook_cell_to_intermediate_dict(notebook_cell)
    assert intermediate_py_str == expected_result


@pytest.mark.parametrize(
    "new_rules_dict,expected_result",
    [
        ({"cell": ["W391", "F401"]}, {"cell": ["W391", "E402", "F401"], "1": ["W391"]}),
        ({"cell": ["noqa"]}, {"cell": ["noqa"], "1": ["W391"]}),
        ({"1": ["noqa"]}, {"cell": ["E402", "F401"], "1": ["noqa"]}),
    ],
)
def test_update_rules_dict(new_rules_dict: Dict[str, List], expected_result: Dict[str, List]):
    total_rules_dict = {"cell": ["E402", "F401"], "1": ["W391"]}
    update_rules_dict(total_rules_dict, new_rules_dict)
    assert sorted(total_rules_dict["cell"]) == sorted(expected_result["cell"])
    assert sorted(total_rules_dict["1"]) == sorted(expected_result["1"])


@pytest.mark.parametrize(
    "source_index,rules_list,expected_result",
    [
        ("foo  # noqa: E402, Fasd401", ["noqa"], "foo  # noqa: \n"),
        (
            "foo  # noqa : E402,      Fasd401 \n",
            ["E402", "F401"],
            "foo  # noqa: E402, F401, Fasd401\n",
        ),
        ("foo  # noqa", ["E402", "F401"], "foo  # noqa: \n"),
        (
            '"foo  # noqa : E402, Fasd401"',
            ["E402", "F401"],
            '"foo  # noqa : E402, Fasd401"  # noqa: E402, F401\n',
        ),
        (
            "foo  # noqa : E402, Fasd401 some randome stuff\n",
            [],
            "foo  # noqa : E402, Fasd401 some randome stuff\n",
        ),
        (
            "foo  # noqa : E402, Fasd401 some randome stuff\n",
            ["E402", "F401"],
            "foo  # noqa : E402, Fasd401 some randome stuff  # noqa: E402, F401\n",
        ),
    ],
)
def test_update_inline_flake8_noqa(source_index: str, rules_list: List, expected_result: str):
    assert update_inline_flake8_noqa(source_index, rules_list) == expected_result


def test_InvalidFlake8TagWarning():
    with pytest.warns(
        InvalidFlake8TagWarning,
        match=(
            "flake8-noqa-line/cell-tags should be of form "
            "'flake8-noqa-cell-<rule1>-<rule2>'|'flake8-noqa-cell'/"
            "'flake8-noqa-line-<line_nr>-<rule1>-<rule2>'|'flake8-noqa-line-<rule1>', "
            "you used: 'user-pattern'"
        ),
    ):
        warnings.warn(InvalidFlake8TagWarning("user-pattern"))
