#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `flake8_nb` package."""

import pytest

from typing import Dict, List, Tuple, Union

from flake8_nb.prepare_file import (
    extract_flake8_tags,
    flake8_tag_to_rules_dict,
    generate_input_name,
    generate_rules_list,
    get_flake8_rules_dict,
    get_inline_flake8_noqa,
    ignore_cell,
    InvalidFlake8TagWarning,
    update_rules_dict,
    update_inline_flake8_noqa,
    warn_wrong_tag_pattern,
)


def test_generate_input_name():
    assert generate_input_name("test_notebook.ipynb", 1) == "test_notebook.ipynb#In[1]"


@pytest.mark.parametrize(
    "line_index,rules_dict,expected_result",
    [
        (
            1,
            {"cell": ["noqa"], "1": ["E402", "F401", "W391"]},
            ["E402", "F401", "W391", "noqa"],
        ),
        (2, {"cell": ["noqa"], "1": ["E402", "F401", "W391"]}, ["noqa"]),
        (2, {"1": ["E402", "F401", "W391"]}, []),
    ],
)
def test_generate_rules_list(
    line_index: int, rules_dict: Dict[str, List], expected_result: List
):
    assert sorted(generate_rules_list(line_index, rules_dict)) == expected_result


@pytest.mark.parametrize(
    "notebook_cell,expected_result",
    [
        (
            {
                "execution_count": 8,
                "metadata": {
                    "tags": ["raises-exception", "flake8-noqa-cell-E402-F401"]
                },
            },
            (8, {"cell": ["E402", "F401"]}),
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
            },
            (9, {"cell": ["noqa"], "1": ["W391", "E402", "F401"]}),
        ),
    ],
)
def test_get_flake8_rules_dict(
    notebook_cell: Dict, expected_result: Tuple[int, Dict[str, List]]
):
    result = get_flake8_rules_dict(notebook_cell)
    assert result[0] == expected_result[0]
    assert sorted(result[1]["cell"]) == sorted(expected_result[1]["cell"])
    if "1" in expected_result:
        assert sorted(result[1]["1"]) == sorted(expected_result[1]["1"])


def test_extract_flake8_tags():
    notebook_cell = {
        "execution_count": 1,
        "metadata": {
            "tags": ["flake8-noqa-cell-E402-F401", "flake8-noqa-cell", "random-tag"]
        },
    }
    expected_result = {
        "input_nr": 1,
        "flake8_tags": ["flake8-noqa-cell-E402-F401", "flake8-noqa-cell"],
    }
    assert extract_flake8_tags(notebook_cell) == expected_result


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
def test_flake8_tag_to_rules_dict(
    flake8_noqa_tag: str, expected_result: Dict[str, List]
):
    if flake8_noqa_tag == "flake8-noqa-line-foo-E402-F401":
        with pytest.warns(InvalidFlake8TagWarning):
            assert flake8_tag_to_rules_dict(flake8_noqa_tag) == expected_result
    else:
        assert flake8_tag_to_rules_dict(flake8_noqa_tag) == expected_result


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
    "code_line,expected_result",
    [
        ("foo  # noqa: E402, Fasd401", ["E402", "Fasd401"]),
        ("foo  # noqa : E402,      Fasd401 \n", ["E402", "Fasd401"]),
        ("foo  # noqa", ["noqa"]),
        ("foo  # noqa   :  ", ["noqa"]),
        ("foo  # noqa    \n", ["noqa"]),
        ('"foo  # noqa : E402, Fasd401"', None),
        ("foo  # noqa : E402, Fasd401 some randome stuff", None),
        ("get_ipython().run_cell_magic('bash', '', 'echo test')\n", None),
    ],
)
def test_get_inline_flake8_noqa(code_line: str, expected_result: Union[str, None]):
    assert get_inline_flake8_noqa(code_line) == expected_result


@pytest.mark.parametrize(
    "new_rules_dict,expected_result",
    [
        ({"cell": ["W391", "F401"]}, {"cell": ["W391", "E402", "F401"], "1": ["W391"]}),
        ({"cell": ["noqa"]}, {"cell": ["noqa"], "1": ["W391"]}),
        ({"1": ["noqa"]}, {"cell": ["E402", "F401"], "1": ["noqa"]}),
    ],
)
def test_update_rules_dict(
    new_rules_dict: Dict[str, List], expected_result: Dict[str, List]
):
    total_rules_dict = {"cell": ["E402", "F401"], "1": ["W391"]}
    update_rules_dict(total_rules_dict, new_rules_dict)
    assert sorted(total_rules_dict["cell"]) == sorted(expected_result["cell"])
    assert sorted(total_rules_dict["1"]) == sorted(expected_result["1"])


@pytest.mark.parametrize(
    "code_line,rules_list,expected_result",
    [
        ("foo  # noqa: E402, Fasd401", ["noqa"], "foo  # noqa: "),
        (
            "foo  # noqa : E402,      Fasd401 \n",
            ["E402", "F401"],
            "foo  # noqa: E402, F401, Fasd401",
        ),
        ("foo  # noqa", ["E402", "F401"], "foo  # noqa: "),
        (
            '"foo  # noqa : E402, Fasd401"',
            ["E402", "F401"],
            '"foo  # noqa : E402, Fasd401"  # noqa: E402, F401',
        ),
        (
            "foo  # noqa : E402, Fasd401 some randome stuff",
            [],
            "foo  # noqa : E402, Fasd401 some randome stuff",
        ),
        (
            "foo  # noqa : E402, Fasd401 some randome stuff",
            ["E402", "F401"],
            "foo  # noqa : E402, Fasd401 some randome stuff  # noqa: E402, F401",
        ),
    ],
)
def test_update_inline_flake8_noqa(
    code_line: str, rules_list: List, expected_result: str
):
    assert update_inline_flake8_noqa(code_line, rules_list) == expected_result


def test_warn_wrong_tag_pattern():
    with pytest.warns(
        InvalidFlake8TagWarning,
        match=(
            "flake8-noqa-line/cell-tags should be of form "
            "'flake8-noqa-cell-<rule1>-<rule2>'|'flake8-noqa-cell'/"
            "'flake8-noqa-line-<line_nr>-<rule1>-<rule2>'|'flake8-noqa-line-<rule1>', "
            "you used: 'user-pattern'"
        ),
    ):
        warn_wrong_tag_pattern("user-pattern")


# foo  # noqa: E402, Fasd401
# foo  # noqa : E402,      Fasd401
# foo  # noqa
# foo  # noqa   :
# foo  # noqa    \n
# "foo  # noqa : E402, Fasd401"
# foo  # noqa : E402, Fasd401 some randome stuff
# get_ipython().run_cell_magic('bash', '', 'echo test')\n
