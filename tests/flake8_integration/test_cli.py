# -*- coding: utf-8 -*-

from .conftest import TempIpynbArgs


from flake8_nb import __version__
from flake8_nb.flake8_integration.cli import (
    get_notebooks_from_args,
    Flake8NbApplication,
)


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
