import os
import subprocess

import pytest

from flake8_nb import FLAKE8_VERSION_TUPLE
from flake8_nb.__main__ import main
from flake8_nb.parsers.notebook_parsers import InvalidNotebookWarning
from flake8_nb.parsers.notebook_parsers import NotebookParser
from tests import TEST_NOTEBOOK_BASE_PATH


@pytest.mark.parametrize("keep_intermediate", [True, False])
@pytest.mark.parametrize(
    "notebook_cell_format,expected_result",
    [
        ("{nb_path}#In[{exec_count}]", "expected_output_exec_count"),
        ("{nb_path}:code_cell#{code_cell_count}", "expected_output_code_cell_count"),
        ("{nb_path}:cell#{total_cell_count}", "expected_output_total_cell_count"),
    ],
)
def test_run_main(
    capsys, keep_intermediate: bool, notebook_cell_format: str, expected_result: str
):
    argv = ["flake8_nb", TEST_NOTEBOOK_BASE_PATH]
    if FLAKE8_VERSION_TUPLE < (3, 8, 0):
        argv = argv[1:]
    if keep_intermediate:
        argv.append("--keep-parsed-notebooks")
    argv += ["--notebook-cell-format", notebook_cell_format]
    argv += ["--exclude", "*.tox/*,*.ipynb_checkpoints*,*/docs/*"]
    with pytest.raises(SystemExit):
        with pytest.warns(InvalidNotebookWarning):
            main(argv)
    captured = capsys.readouterr()
    result_output = captured.out
    result_list = result_output.replace("\r", "").split("\n")
    result_list.remove("")
    expected_result_path = os.path.join(
        os.path.dirname(__file__), "data", f"{expected_result}.txt"
    )
    with open(expected_result_path) as result_file:
        expected_result_list = result_file.readlines()
    assert len(expected_result_list) == len(result_list)
    for expected_result in expected_result_list:
        assert any(result.endswith(expected_result.rstrip("\n")) for result in result_list)

    if keep_intermediate:
        assert os.path.exists(NotebookParser.temp_path)
        NotebookParser.clean_up()


def test_run_main_all_excluded(capsys):
    argv = ["flake8_nb", TEST_NOTEBOOK_BASE_PATH]
    if FLAKE8_VERSION_TUPLE < (3, 8, 0):
        argv = argv[1:]
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
@pytest.mark.parametrize(
    "notebook_cell_format,expected_result",
    [
        ("{nb_path}#In[{exec_count}]", "expected_output_exec_count"),
        ("{nb_path}:code_cell#{code_cell_count}", "expected_output_code_cell_count"),
        ("{nb_path}:cell#{total_cell_count}", "expected_output_total_cell_count"),
    ],
)
def test_syscall(
    cli_entrypoint: str, keep_intermediate: bool, notebook_cell_format: str, expected_result: str
):
    argv = [cli_entrypoint, TEST_NOTEBOOK_BASE_PATH]
    if keep_intermediate:
        argv.append("--keep-parsed-notebooks")
    argv += ["--notebook-cell-format", notebook_cell_format]
    argv += ["--exclude", "*.tox/*,*.ipynb_checkpoints*,*/docs/*"]
    proc = subprocess.Popen(argv, stdout=subprocess.PIPE, universal_newlines=True)
    result_list = [str(line) for line in proc.stdout]
    expected_result_path = os.path.join(
        os.path.dirname(__file__), "data", f"{expected_result}.txt"
    )
    with open(expected_result_path) as result_file:
        expected_result_list = result_file.readlines()

    print("\n".join(expected_result_list))
    print("#" * 80)
    print("\n".join(result_list))
    assert len(expected_result_list) == len(result_list)

    for expected_result in expected_result_list:
        assert any(result.endswith(expected_result) for result in result_list)
