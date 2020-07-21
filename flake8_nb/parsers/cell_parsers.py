# -*- coding: utf-8 -*-

"""Module containing parsers for notebook cells.
This also inclues parsers for the cell and inline tags.
It heavily utilizes the mutability of lists."""

import re
import warnings
from typing import Dict, List

FLAKE8_TAG_PATTERN = re.compile(
    r"^flake8-noqa-(cell-(?P<cell_rules>(\w+\d+-?)+)"
    r"|line-(?P<line_nr>\d+)-(?P<line_rules>(\w+\d+-?)+))$"
    r"|^(?P<ignore_cell>flake8-noqa-cell)$"
    r"|^flake8-noqa-line-(?P<ignore_line_nr>\d+)$"
)

FLAKE8_INLINE_TAG_PATTERN = re.compile(
    r"^.*?(#(?P<flake8_inline_tags>(\s*flake8-noqa-(cell(-\w+\d+)*|line-\d+(-\w+\d+)*))+))\s*$",
    re.DOTALL,
)

FLAKE8_NOQA_INLINE_PATTERN = re.compile(
    r"^.+?\s*[#]\s*noqa\s*[:]"
    r"(?P<flake8_noqa_rules>(\s*\w+\d+[,]?\s*)+)$"
    r"|^.+?\s*(?P<has_flake8_noqa_all>[#]\s*noqa\s*[:]?\s*)$"
)

FLAKE8_NOQA_INLINE_REPLACE_PATTERN = re.compile(
    r"^(?P<source_code>.+?)\s*(?P<flake8_noqa>[#]\s*noqa\s*[:]?.*)$"
)


class InvalidFlake8TagWarning(UserWarning):
    """
    Warning which is thrown, when a cell tag starts with
    'flake8-noqa-' but doesn't match the correct pattern
    needed for cell tags. This is used to show users that
    they have a typo in their tags.
    """

    def __init__(self, flake8_tag, *args, **kwargs):
        super().__init__(
            "flake8-noqa-line/cell-tags should be of form "
            "'flake8-noqa-cell-<rule1>-<rule2>'|'flake8-noqa-cell'/"
            "'flake8-noqa-line-<line_nr>-<rule1>-<rule2>'|'flake8-noqa-line-<rule1>', "
            f"you used: '{flake8_tag}'"
        )


def extract_flake8_tags(notebook_cell: Dict) -> List[str]:
    """
    Exctracts all tag that start with 'flake8-noqa-' from a cell.

    Parameters
    ----------
    notebook_cell : Dict
        Dict representation of a notebook cell as parsed from JSON.

    Returns
    -------
    List[str]
        List of all tags in the given cell, which started with 'flake8-noqa-'.
    """
    flake8_tags = []
    for tag in notebook_cell["metadata"].get("tags", []):
        if tag.startswith("flake8-noqa-"):
            flake8_tags.append(tag)
    return flake8_tags


def extract_flake8_inline_tags(notebook_cell: Dict) -> List[str]:
    """
    Extracts flake8-tags which were used as comment in a cell.

    Parameters
    ----------
    notebook_cell : Dict
        Dict representation of a notebook cell as parsed from JSON.

    Returns
    -------
    List[str]
        List of all inline tags in the given cell,
        which matched ``FLAKE8_INLINE_TAG_PATTERN``.
    """
    flake8_inline_tags = []
    for source_line in notebook_cell["source"]:
        match = re.match(FLAKE8_INLINE_TAG_PATTERN, source_line)
        if match and match.group("flake8_inline_tags"):
            for tag in match.group("flake8_inline_tags").split(" "):
                tag = tag.strip()
                if tag:
                    flake8_inline_tags.append(tag)
    return flake8_inline_tags


def extract_inline_flake8_noqa(source_line: str) -> List[str]:
    """
    Extracts flake8 noqa rules from normal flake8 comments and
    returns the as list.

    Parameters
    ----------
    source_line : str
        Single line of sourcecode from a cell.

    Returns
    -------
    List[str]
        List of flake8 rules.
    """
    match = re.match(FLAKE8_NOQA_INLINE_PATTERN, source_line)
    if match:
        flake8_noqa_rules_str = match.group("flake8_noqa_rules")
        if flake8_noqa_rules_str:
            flake8_noqa_rules = flake8_noqa_rules_str.split(",")
            return [line.strip() for line in flake8_noqa_rules]
        elif match.group("has_flake8_noqa_all"):  # pragma: no branch
            return ["noqa"]
    return []


def flake8_tag_to_rules_dict(flake8_tag: str) -> Dict[str, List[str]]:
    """
    Parses a flake8 tag to a ``rules_dict``.
    ``rules_dict`` contains lists of rules, depending on if the
    tag is a cell or a line tag.

    Parameters
    ----------
    flake8_tag : str
        String of a flake8-tag.

    Returns
    -------
    Dict[str, List[str]]
        Dict with cell and line rules. Line rules have the line number
        as key  and cell rules have 'cell as key'.

    See Also
    --------
    get_flake8_rules_dict
    """
    match = re.match(FLAKE8_TAG_PATTERN, flake8_tag)
    if match:
        if match.group("cell_rules"):
            cell_rules_str = match.group("cell_rules")
            cell_rules = cell_rules_str.split("-")
            return {"cell": cell_rules}
        elif match.group("ignore_cell"):
            return {"cell": ["noqa"]}
        elif match.group("line_nr") and match.group("line_rules"):
            line_nr = str(match.group("line_nr"))
            line_rules_str = match.group("line_rules")
            line_rules = line_rules_str.split("-")
            return {line_nr: line_rules}
        elif match.group("ignore_line_nr"):  # pragma: no branch
            line_nr = str(match.group("ignore_line_nr"))
            return {line_nr: ["noqa"]}
    warnings.warn(InvalidFlake8TagWarning(flake8_tag))
    return {}


def update_rules_dict(
    total_rules_dict: Dict[str, List], new_rules_dict: Dict[str, List]
) -> None:
    """
    Updates the rules dict ``total_rules_dict`` with ``new_rules_dict``.
    If any entry of a key is 'noqa' (ignore all), the rules will be
    set to be only 'noqa'.

    Parameters
    ----------
    total_rules_dict : Dict[str, List]
        ``rules_dict`` which should be updated.
    new_rules_dict : Dict[str, List]
        ``rules_dict`` which should be used to update ``total_rules_dict``.

    Returns
    -------
    Dict[str, List]
        Updated ``total_rules_dict``.

    See Also
    --------
    flake8_tag_to_rules_dict, get_flake8_rules_dict
    """
    for key, new_rules in new_rules_dict.items():
        old_rules = total_rules_dict.get(key, [])
        if "noqa" in old_rules + new_rules:
            total_rules_dict[key] = ["noqa"]
        else:
            total_rules_dict[key] = list(set(old_rules + new_rules))


def get_flake8_rules_dict(notebook_cell: Dict) -> Dict[str, List]:
    """
    Parses all flake8 tags of a cell to a ``rules_dict``.
    ``rules_dict`` contains lists of rules, depending on if the
    tag is a cell or a line tag.

    Parameters
    ----------
    notebook_cell : Dict
        Dict representation of a notebook cell as parsed from JSON.

    Returns
    -------
    Dict[str, List]
        Dict with all cell and line rules. Line rules have the line number
        as key  and cell rules have 'cell as key'.

    See Also
    --------
    flake8_tag_to_rules_dict, update_rules_dict
    """
    flake8_tags = extract_flake8_tags(notebook_cell)
    flake8_inline_tags = extract_flake8_inline_tags(notebook_cell)
    total_rules_dict: Dict[str, List] = {}
    for flake8_tag in set(flake8_tags + flake8_inline_tags):
        new_rules_dict = flake8_tag_to_rules_dict(flake8_tag)
        update_rules_dict(total_rules_dict, new_rules_dict)
    return total_rules_dict


def generate_rules_list(source_index: int, rules_dict: Dict[str, List]) -> List[str]:
    """
    Generates a List of rules from ``rules_dict``, which should be
    applied to the line at ``source_index``.

    Parameters
    ----------
    source_index : int
        Index of the source code line.
    rules_dict : Dict[str, List]
        Dict containing lists of rules, depending on if the tag is a
        cell or a line tag.

    Returns
    -------
    List[str]
        List of rules which should be applied to the line at ``source_index``.

    See Also
    --------
    flake8_tag_to_rules_dict, get_flake8_rules_dict
    """
    line_rules = rules_dict.get(str(source_index + 1), [])
    cell_rules = rules_dict.get("cell", [])
    return line_rules + cell_rules


def update_inline_flake8_noqa(source_line: str, rules_list: List[str]) -> str:
    """
    Updates ``source_line`` with flake8 noqa comments.
    This is done extraction flake8-tags as well as inline flake8
    comments.

    Parameters
    ----------
    source_line : str
        Single line of sourcecode from a cell.
    rules_list : List[str]
        List of rules which should be applied to ``source_line``.

    Returns
    -------
    str
        ``source_line`` with flake8 noqa comments.

    See Also
    --------
    generate_rules_list
    """
    inline_flake8_noqa = extract_inline_flake8_noqa(source_line)
    source_line = source_line.rstrip("\n")
    if inline_flake8_noqa:
        rules_list = list(set(inline_flake8_noqa + rules_list))
        source_line = re.sub(
            FLAKE8_NOQA_INLINE_REPLACE_PATTERN, r"\g<source_code>", source_line
        )
    rules_list = sorted(rules_list)
    if "noqa" in rules_list:
        noqa_str = ""
    else:
        noqa_str = ", ".join(rules_list)
    if rules_list:
        return f"{source_line}  # noqa: {noqa_str}\n"
    else:
        return f"{source_line}\n"


def notebook_cell_to_intermediate_dict(notebook_cell: Dict) -> Dict:
    r"""
    Parses ``notebook_cell`` to a dict which can later be written to a
    intermediate_py_file.

    Parameters
    ----------
    notebook_cell : Dict
        Dict representation of a notebook cell as parsed from JSON.

    Returns
    -------
    Dict
        Dict which has the keys 'code', 'input_name' and 'code'.
        ``code``,``input_name`` is a str of the code cells ``In[\d\*]`` name and ``lines_of_code``
        is the number of lines of corresponding parsed parsed notebook cell.

    See Also
    --------
    update_inline_flake8_noqa, flake8_nb.parsers.notebook_parsers.create_intermediate_py_file
    """
    updated_source_lines = []
    input_nr = notebook_cell["execution_count"]
    rules_dict = get_flake8_rules_dict(notebook_cell)
    for line_index, source_line in enumerate(notebook_cell["source"]):
        rules_list = generate_rules_list(line_index, rules_dict)
        updated_source_line = update_inline_flake8_noqa(source_line, rules_list)
        updated_source_lines.append(updated_source_line)
    if input_nr is None:
        input_nr = " "
    input_name = f"In[{input_nr}]"
    return {
        "code": f"# {input_name}\n\n\n{''.join(updated_source_lines)}\n\n",
        "input_name": input_name,
        "lines_of_code": len(updated_source_lines) + 5,
    }
