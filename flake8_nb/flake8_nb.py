# -*- coding: utf-8 -*-

"""Main module."""
from . import __version__
import json
import logging
from ast import Module
from optparse import Values
from flake8.options.manager import OptionManager

# import re


def ignore_cell(notebook_cell):
    if notebook_cell["cell_type"] != "code":
        return True
    elif not notebook_cell["source"]:
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
                if source_line.startswith(("%", "?", "!")) or source_line.endswith(
                    ("?", "?\n")
                ):
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


class Flake8Notebook:
    name = "flake8_nb"
    version = __version__
    use_flake8_nb = False

    def __init__(self, tree: Module, filename: str):
        self.filename = filename
        self.tree = tree

    @classmethod
    def add_options(cls, parser: OptionManager):
        parser.add_option(
            short_option_name="--nb",
            long_option_name="--check_notebook",
            action="store_true",
            parse_from_config=True,
            help="Enables testing of jupyter/iPython notebooks",
        )
        # logging.warn(f"OPTIONS DICT: {parser.config_options_dict['filename']}")

    @classmethod
    def parse_options(cls, option_manager: OptionManager, options: Values, args):
        logging.warn(f"OPTIONS: {options}")
        if options.check_notebook:
            options.ensure_value("filename", ["*.ipynb#In*"])
            # options.filename = options.filename.append("ipynb")
            # options.filename = options.filename.append("*.ipynb#In*")
            # options.__dict__["filename"] = "*.ipynb#In*, *.py"
            with open("testing/test_notebook.ipynb#In[1]", "w+") as test:
                test.write("%%bash")

            logging.warn(f"args: {args}")
            logging.warn(f"option_manager TYPE: {type(option_manager)}")
            logging.warn(
                f'options.filename VALUE: {option_manager.config_options_dict["filename"]}'
            )
            cls.use_flake8_nb = options.check_notebook

    def run(self):
        logging.warn(f"FILENAME: {self.filename}")
        # logging.warn(f"TREE: {self.tree.body}")
        if self.filename.endswith("flake8_nb.py"):
            # raise Exception("FOOO")
            # yield [Exception(1, 1, "MESSAGE TEXT", type(self))]
            pass
        yield (1, 1, "MESSAGE TEXT", type(self))
