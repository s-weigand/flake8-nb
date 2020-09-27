import os
import subprocess

import pytest

from flake8_nb.__main__ import main
from flake8_nb.parsers.notebook_parsers import InvalidNotebookWarning
from flake8_nb.parsers.notebook_parsers import NotebookParser

from . import TEST_NOTEBOOK_BASE_PATH


@pytest.mark.parametrize("keep_intermediate", [True, False])
def test_run_main(capsys, keep_intermediate: bool):
    argv = ["flake8_nb", TEST_NOTEBOOK_BASE_PATH]
    if keep_intermediate:
        argv.append("--keep-parsed-notebooks")
    argv += ["--exclude", "*.tox/*,*.ipynb_checkpoints*,*/docs/*"]
    with pytest.raises(SystemExit):
        with pytest.warns(InvalidNotebookWarning):
            main(argv)
    captured = capsys.readouterr()
    result_output = captured.out
    result_list = result_output.replace("\r", "").split("\n")
    result_list.remove("")
    expected_result_path = os.path.join(os.path.dirname(__file__), "data", "expected_output.txt")
    with open(expected_result_path) as result_file:
        expected_result_list = result_file.readlines()
    assert len(expected_result_list) == len(result_list)
    for expected_result in expected_result_list:
        assert any([result.endswith(expected_result.rstrip("\n")) for result in result_list])

    if keep_intermediate:
        assert os.path.exists(NotebookParser.temp_path)
        NotebookParser.clean_up()


def test_run_main_all_excluded(capsys):
    argv = ["flake8_nb", TEST_NOTEBOOK_BASE_PATH]
    argv += [
        "--exclude",
        f"*.tox/*,*.ipynb_checkpoints*,*/docs/*,{TEST_NOTEBOOK_BASE_PATH}",
    ]
    with pytest.raises(SystemExit):
        with pytest.warns(InvalidNotebookWarning):
            main(argv)
    captured = capsys.readouterr()
    result_output = captured.out
    result_list = result_output.replace("\r", "").split("\n")
    result_list.remove("")
    assert len(result_list) == 0


@pytest.mark.parametrize("keep_intermediate", [True, False])
@pytest.mark.parametrize("cli_entrypoint", ["flake8_nb", "flake8-nb"])
def test_syscall(cli_entrypoint: str, keep_intermediate: bool):
    argv = [cli_entrypoint, TEST_NOTEBOOK_BASE_PATH]
    if keep_intermediate:
        argv.append("--keep-parsed-notebooks")
    argv += ["--exclude", "*.tox/*,*.ipynb_checkpoints*,*/docs/*"]
    proc = subprocess.Popen(argv, stdout=subprocess.PIPE, universal_newlines=True)
    result_list = []
    for line in proc.stdout:
        result_list.append(str(line))
    expected_result_path = os.path.join(os.path.dirname(__file__), "data", "expected_output.txt")
    with open(expected_result_path) as result_file:
        expected_result_list = result_file.readlines()

    assert len(expected_result_list) == len(result_list)

    for expected_result in expected_result_list:
        assert any([result.endswith(expected_result) for result in result_list])
