# -*- coding: utf-8 -*-

"""Main module."""
import json
from typing import Dict, List, Tuple, Union
import warnings
from nbconvert.filters import ipython2python

import re

import functools  # noqa:


FLAKE8_TAG_PATTERN = re.compile(
    r"^flake8-noqa-(cell-(?P<cell_rules>(\w+\d+-?)+)"
    r"|line-(?P<line_nr>\d+)-(?P<line_rules>(\w+\d+-?)+))$"
    r"|^(?P<ignore_cell>flake8-noqa-cell)$"
    r"|^flake8-noqa-line-(?P<ignore_line_nr>\d+)$"
)

HAS_FLAKE8_NOQA_PATTERN = re.compile(
    r"^.+?\s*(?P<has_flake8_noqa_rules>[#]\s*noqa\s*[:]"
    r"(\s*\w+\d+[,]?\s*)+)(\n)?$"
    r"|^.+?\s*(?P<has_flake8_noqa_all>[#]\s*noqa\s*[:]?\s*)(\n)?$",
    re.DOTALL,
)


class InvalidFlake8TagWarning(UserWarning):
    pass


def warn_wrong_tag_pattern(flake8_tag: str):
    warnings.warn(
        "flake8-noqa-line/cell-tags should be of form "
        "'flake8-noqa-cell-<rule1>-<rule2>'|'flake8-noqa-cell'/"
        "'flake8-noqa-line-<line_nr>-<rule1>-<rule2>'|'flake8-noqa-line-<rule1>', "
        f"you used: '{flake8_tag}'",
        InvalidFlake8TagWarning,
    )


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
        if tag.startswith("flake8-noqa"):
            flake8_tags.append(tag)
    return {"input_nr": input_nr, "flake8_tags": flake8_tags}


def flake8_tag_to_rules_dict(flake8_tag: str) -> Dict[str, List]:
    match = re.match(FLAKE8_TAG_PATTERN, flake8_tag)
    if match:
        if match.group("cell_rules"):
            cell_rules = match.group("cell_rules")
            cell_rules = cell_rules.split("-")
            return {"cell": cell_rules}
        elif match.group("ignore_cell"):
            return {"cell": ["noqa"]}
        elif match.group("line_nr") and match.group("line_rules"):
            line_nr = str(match.group("line_nr"))
            line_rules = match.group("line_rules")
            line_rules = line_rules.split("-")
            return {line_nr: line_rules}
        elif match.group("ignore_line_nr"):
            line_nr = str(match.group("ignore_line_nr"))
            return {line_nr: ["noqa"]}
    warn_wrong_tag_pattern(flake8_tag)
    return {}


def update_rules_dict(
    total_rules_dict: Dict[str, List], new_rules_dict: Dict[str, List]
) -> Dict[str, List]:
    for key, new_rules in new_rules_dict.items():
        old_rules = total_rules_dict.get(key, [])
        if "noqa" in old_rules + new_rules:
            total_rules_dict[key] = ["noqa"]
        else:
            total_rules_dict[key] = list(set(old_rules + new_rules))


def get_flake8_rules_dict(notebook_cell: Dict) -> Tuple[int, Dict[str, List]]:
    flake8_tags = extract_flake8_tags(notebook_cell)
    total_rules_dict = {}
    for flake8_tag in flake8_tags["flake8_tags"]:
        new_rules_dict = flake8_tag_to_rules_dict(flake8_tag)
        update_rules_dict(total_rules_dict, new_rules_dict)
    return flake8_tags["input_nr"], total_rules_dict


def has_flake8_noqa(code_line: str) -> Union[str, None]:
    match = re.match(HAS_FLAKE8_NOQA_PATTERN, code_line)
    if match:
        if match.group("has_flake8_noqa_rules"):
            return "rules"
        elif match.group("has_flake8_noqa_all"):
            return "all"
