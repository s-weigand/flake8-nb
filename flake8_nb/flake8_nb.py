# -*- coding: utf-8 -*-

"""Main module."""

import json
import re

def ignore_cell(notebook_cell):
    if notebook_cell["cell_type"] != "code":
        return True
    elif not cell["source"]:
        return True
    elif "flake8-noqa" in notebook_cell["metadata"].get("tags", []):
        return True

    
def get_clean_notebook(notebook_path):
    with open(notebook_path) as notebook_file:
        notebook_cells = json.load(notebook_file)["cells"]
        
    for index, cell in list(enumerate(notebook_cells))[::-1]:
        if ignore_cell(cell):
            notebook_cells.pop(index)
        else:
            cell_source = list(enumerate(cell["source"]))[::-1]
            for source_line_index, source_line in cell_source:
                if source_line.startswith(("%", "?", "!")) or source_line.endswith(("?", "?\n")):
                    cell["source"].pop(source_line_index)
            if not cell["source"]:
                notebook_cells.pop(index)
    return notebook_cells


def generate_input_name(notebook_path, input_nr):
    return f"{notebook_path}#In[{input_nr}]"


def strip_newline(souce_line):
    return souce_line.rstrip("\n")


def add_newline(souce_line):
    return f"{souce_line}\n"


def extract_flake8_tags(notebook_cell):
    input_nr = notebook_cell["execution_count"]
    flake8_tags = []
    for tag in notebook_cell["metadata"].get("tags", []):
        print(tag)
        if tag.startswith("flake8-noqa"):
            flake8_tags.append(tag)
    return {"input_nr": input_nr, "flake8_tags": flake8_tags}