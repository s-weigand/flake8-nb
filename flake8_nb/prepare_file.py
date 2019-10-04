# -*- coding: utf-8 -*-

"""Main module."""
import json
import re

# import tempfile
from typing import Dict, List, Tuple, Union
import warnings

from nbconvert.filters import ipython2python


FLAKE8_TAG_PATTERN = re.compile(
    r"^flake8-noqa-(cell-(?P<cell_rules>(\w+\d+-?)+)"
    r"|line-(?P<line_nr>\d+)-(?P<line_rules>(\w+\d+-?)+))$"
    r"|^(?P<ignore_cell>flake8-noqa-cell)$"
    r"|^flake8-noqa-line-(?P<ignore_line_nr>\d+)$"
)

FLAKE8_NOQA_INLINE_PATTERN = re.compile(
    r"^.+?\s*[#]\s*noqa\s*[:]"
    r"(?P<flake8_noqa_rules>(\s*\w+\d+[,]?\s*)+)(\n)?$"
    r"|^.+?\s*(?P<has_flake8_noqa_all>[#]\s*noqa\s*[:]?\s*)(\n)?$"
)

FLAKE8_NOQA_INLINE_REPLACE_PATTERN = re.compile(
    r"^(?P<source_code>.+?)\s*(?P<flake8_noqa>[#]\s*noqa\s*[:]?.*)(\n)?$"
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
        elif match.group("ignore_line_nr"):  # pragma: no branch
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


def generate_rules_list(line_index: int, rules_dict: Dict[str, List]) -> List:
    line_rules = rules_dict.get(str(line_index), [])
    cell_rules = rules_dict.get("cell", [])
    return line_rules + cell_rules


def get_inline_flake8_noqa(code_line: str) -> List:
    match = re.match(FLAKE8_NOQA_INLINE_PATTERN, code_line)
    if match:
        flake8_noqa_rules = match.group("flake8_noqa_rules")
        if flake8_noqa_rules:
            flake8_noqa_rules = flake8_noqa_rules.split(",")
            return [line.strip() for line in flake8_noqa_rules]
        elif match.group("has_flake8_noqa_all"):  # pragma: no branch
            return ["noqa"]
    else:
        return []


def update_inline_flake8_noqa(source_line: str, rules_list: List) -> str:
    inline_flake8_noqa = get_inline_flake8_noqa(source_line)
    if inline_flake8_noqa:
        rules_list = set(inline_flake8_noqa + rules_list)
        source_line = re.sub(
            FLAKE8_NOQA_INLINE_REPLACE_PATTERN, r"\g<source_code>", source_line
        )
    rules_list = sorted(list(rules_list))
    if "noqa" in rules_list:
        noqa_str = ""
    else:
        noqa_str = ", ".join(rules_list)
    if rules_list:
        return f"{source_line}  # noqa: {noqa_str}"
    else:
        return source_line
