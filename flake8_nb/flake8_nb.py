# -*- coding: utf-8 -*-

"""Main module."""
import json
from typing import Dict, List, Tuple, Union
import warnings

# logging.basicConfig(level=logging.DEBUG)

import re

# python 3.6 compat
try:
    from re import Pattern as re_Pattern
except ImportError:
    re_Pattern = type(re.compile("", 0))

import functools  # noqa


class InvalidFlake8TagWarning(UserWarning):
    pass


def warn_wrong_tag_pattern(flake8_tag: str):
    warnings.warn(
        "flake8-noqa-line/cell-tags should be of form "
        "'flake8-noqa-cell-<rule1>-<rule2>'/"
        "'flake8-noqa-line-<line_nr>-<rule1>-<rule2>', "
        f"you used: '{flake8_tag}'",
        InvalidFlake8TagWarning,
    )


def ignore_cell(notebook_cell: Dict):
    if notebook_cell["cell_type"] != "code":
        return True
    elif not notebook_cell["source"]:
        return True
    elif "flake8-noqa" in notebook_cell["metadata"].get("tags", []):
        return True


def get_clean_notebook(notebook_path: str):
    with open(notebook_path) as notebook_file:
        notebook_cells = json.load(notebook_file)["cells"]

    for index, cell in list(enumerate(notebook_cells))[::-1]:
        if ignore_cell(cell):
            notebook_cells.pop(index)
        else:
            cell_source = list(enumerate(cell["source"]))[::-1]
            for source_line_index, source_line in cell_source:
                if source_line.startswith(("%", "?", "!")) or source_line.endswith(
                    ("?", "?\n")
                ):
                    cell["source"].pop(source_line_index)
            if not cell["source"]:
                notebook_cells.pop(index)
    return notebook_cells


def generate_input_name(notebook_path: str, input_nr: Union[int, str]):
    return f"{notebook_path}#In[{input_nr}]"


def strip_newline(souce_line: str):
    return souce_line.rstrip("\n")


def add_newline(souce_line: str):
    return f"{souce_line}\n"


def extract_flake8_tags(notebook_cell: Dict):
    input_nr = notebook_cell["execution_count"]
    flake8_tags = []
    for tag in notebook_cell["metadata"].get("tags", []):
        print(tag)
        if tag.startswith("flake8-noqa"):
            flake8_tags.append(tag)
    return {"input_nr": input_nr, "flake8_tags": flake8_tags}


def flake8_tag_to_rules_dict(
    flake8_tag_regex: re_Pattern, flake8_tag: str
) -> Dict[str, List]:
    match = re.match(flake8_tag_regex, flake8_tag)
    if match:
        if match.group("cell_rules"):
            cell_rules = match.group("cell_rules")
            cell_rules = cell_rules.split("-")
            return {"cell": cell_rules}
        elif match.group("line_nr") and match.group("line_rules"):
            line_nr = str(match.group("line_nr"))
            line_rules = match.group("line_rules")
            line_rules = line_rules.split("-")
            return {line_nr: line_rules}
    warn_wrong_tag_pattern(flake8_tag)
    return {}


def update_rules_dict(
    total_rules_dict: Dict[str, List], new_rules_dict: Dict[str, List]
) -> Dict[str, List]:
    for key, rules in new_rules_dict.items():
        total_rules_dict[key] = total_rules_dict.get(key, []) + rules


def get_flake8_rules_dict(notebook_cell: Dict) -> Tuple[int, Dict[str, List]]:
    flake8_tags = extract_flake8_tags(notebook_cell)
    flake8_tag_pattern = (
        r"flake8-noqa-(cell-(?P<cell_rules>(\w+\d+-?)+)|"
        r"line-(?P<line_nr>\d+)-(?P<line_rules>(\w+\d+-?)+))"
    )
    flake8_tag_regex = re.compile(flake8_tag_pattern)
    total_rules_dict = {}
    for flake8_tag in flake8_tags["flake8_tags"]:
        new_rules_dict = flake8_tag_to_rules_dict(flake8_tag_regex, flake8_tag)
        update_rules_dict(total_rules_dict, new_rules_dict)
    return flake8_tags["input_nr"], total_rules_dict
