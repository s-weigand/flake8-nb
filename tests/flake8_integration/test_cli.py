import contextlib
import os
import re

import flake8
import pytest

from flake8_nb import FLAKE8_VERSION_TUPLE
from flake8_nb import __version__
from flake8_nb.flake8_integration.cli import Flake8NbApplication
from flake8_nb.flake8_integration.cli import get_notebooks_from_args
from flake8_nb.flake8_integration.cli import hack_option_manager_generate_versions
from flake8_nb.parsers.notebook_parsers import InvalidNotebookWarning
from flake8_nb.parsers.notebook_parsers import NotebookParser
from tests.flake8_integration.conftest import TempIpynbArgs


def test_get_notebooks_from_args(temp_ipynb_args: TempIpynbArgs):
    orig_args, (expected_args, expected_nb_list) = temp_ipynb_args.get_args_and_result()
    args, nb_list = get_notebooks_from_args(
        orig_args, exclude=["*.tox/*", ".ipynb_checkpoints", "*/docs/*"]
    )
    assert sorted(args) == sorted(expected_args)
    assert sorted(nb_list) == sorted(expected_nb_list)


def test_hack_option_manager_generate_versions():
    pattern = re.compile(rf"flake8: {flake8.__version__}, original_input")

    def test_func(*args, **kwargs):
        return "original_input"

    hacked_output = hack_option_manager_generate_versions(test_func)()
    assert re.match(pattern, hacked_output) is not None


def test_Flake8NbApplication__generate_versions():
    generate_versions_pattern = re.compile(
        rf"flake8: {flake8.__version__}(, [\w\-_]+: \d+\.\d+\.\d+)+"
    )
    generate_epilog_pattern = re.compile(
        rf"Installed plugins: flake8: {flake8.__version__}(, [\w\-_]+: \d+\.\d+\.\d+)+"
    )
    orig_args = [os.path.join("tests", "data", "notebooks")]
    app = Flake8NbApplication()
    app.initialize(orig_args)

    if FLAKE8_VERSION_TUPLE < (5, 0, 0):
        app.option_manager.generate_epilog()

        hacked_generate_versions = app.option_manager.generate_versions()
        assert re.match(generate_versions_pattern, hacked_generate_versions) is not None

    hacked_generate_epilog: str = app.option_manager.parser.epilog  # type: ignore

    assert re.match(generate_epilog_pattern, hacked_generate_epilog) is not None


def test_Flake8NbApplication__hack_flake8_program_and_version():
    app = Flake8NbApplication()
    app.initialize([])
    program = "flake8_nb"

    assert app.program == program
    assert app.version == __version__
    assert app.option_manager.parser.prog == program
    assert app.option_manager.parser.version == __version__  # type: ignore
    assert app.option_manager.program_name == program
    assert app.option_manager.version == __version__


def test_Flake8NbApplication__option_defaults():
    app = Flake8NbApplication()
    app.initialize([])

    option_dict = app.option_manager.config_options_dict
    assert option_dict["format"].default == "default_notebook"
    assert option_dict["filename"].default == "*.py,*.ipynb_parsed"
    assert option_dict["exclude"].default.endswith(",.ipynb_checkpoints")  # type: ignore
    assert option_dict["keep_parsed_notebooks"].default is False


@pytest.mark.filterwarnings(InvalidNotebookWarning)
def test_Flake8NbApplication__hack_args(temp_ipynb_args: TempIpynbArgs):
    orig_args, (expected_args, _) = temp_ipynb_args.get_args_and_result()
    result = Flake8NbApplication.hack_args(
        orig_args, exclude=["*.tox/*", "*.ipynb_checkpoints*", "*/docs/*"]
    )
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
        orig_args = []
        if keep_parsed_notebooks is True:
            orig_args += ["--keep-parsed-notebooks"]
        app = Flake8NbApplication()
        app.initialize([*orig_args, os.path.join("tests", "data", "notebooks")])
        temp_path = NotebookParser.temp_path
        with contextlib.suppress(SystemExit):
            app.exit()
    assert os.path.exists(temp_path) == keep_parsed_notebooks
    NotebookParser.clean_up()
