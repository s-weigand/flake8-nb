# -*- coding: utf-8 -*-

import os

import pytest

from flake8_nb import __version__
from flake8_nb.flake8_integration.cli import (
    Flake8NbApplication,
    get_notebooks_from_args,
)
from flake8_nb.parsers.notebook_parsers import InvalidNotebookWarning, NotebookParser

from .conftest import TempIpynbArgs


def test_get_notebooks_from_args(temp_ipynb_args: TempIpynbArgs):
    orig_args, (expected_args, expected_nb_list) = temp_ipynb_args.get_args_and_result()
    args, nb_list = get_notebooks_from_args(orig_args)
    assert sorted(args) == sorted(expected_args)
    assert sorted(nb_list) == sorted(expected_nb_list)


def test_Flake8NbApplication__hack_flake8_program_and_version():
    app = Flake8NbApplication()
    program = "flake8_nb"

    assert app.program == program
    assert app.version == __version__
    assert app.option_manager.parser.prog == program
    assert app.option_manager.parser.version == __version__
    assert app.option_manager.program_name == program
    assert app.option_manager.version == __version__


def test_Flake8NbApplication__option_defaults():
    app = Flake8NbApplication()

    option_dict = app.option_manager.config_options_dict
    assert option_dict["format"].default == "default_notebook"
    assert option_dict["filename"].default == "*.py,*.ipynb_parsed"
    assert option_dict["exclude"].default.endswith(",*.ipynb_checkpoints/*")
    assert option_dict["keep_parsed_notebooks"].default is False


@pytest.mark.filterwarnings(InvalidNotebookWarning)
def test_Flake8NbApplication__hack_args(temp_ipynb_args: TempIpynbArgs):
    orig_args, (expected_args, _) = temp_ipynb_args.get_args_and_result()
    result = Flake8NbApplication.hack_args(orig_args)
    expected_parsed_nb_list = NotebookParser.intermediate_py_file_paths

    assert result == expected_args + expected_parsed_nb_list


@pytest.mark.filterwarnings(InvalidNotebookWarning)
def test_Flake8NbApplication__parse_configuration_and_cli():
    orig_args = [os.path.join("tests", "data", "notebooks")]
    app = Flake8NbApplication()
    # parse_configuration_and_cli is called by initialize
    app.initialize(orig_args)
    expected_parsed_nb_list = NotebookParser.intermediate_py_file_paths

    assert app.args == orig_args + expected_parsed_nb_list


@pytest.mark.parametrize("keep_parsed_notebooks", [False, True])
def test_Flake8NbApplication__exit(keep_parsed_notebooks: bool):
    with pytest.warns(InvalidNotebookWarning):
        orig_args = [os.path.join("tests", "data", "notebooks")]
        app = Flake8NbApplication()
        app.set_flake8_option("--keep-parsed-notebooks", default=keep_parsed_notebooks)
        app.initialize(orig_args)
        temp_path = NotebookParser.temp_path
        try:
            app.exit()
        except SystemExit:
            pass

    assert os.path.exists(temp_path) == keep_parsed_notebooks
    NotebookParser.clean_up()
