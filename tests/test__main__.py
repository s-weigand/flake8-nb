import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from _pytest.capture import CaptureFixture
from _pytest.monkeypatch import MonkeyPatch
from flake8 import __version__ as flake_version

from flake8_nb import FLAKE8_VERSION_TUPLE
from flake8_nb import __version__
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
    argv = ["flake8_nb"]
    if keep_intermediate:
        argv.append("--keep-parsed-notebooks")
    argv += ["--notebook-cell-format", notebook_cell_format]
    argv += ["--exclude", "*.tox/*,*.ipynb_checkpoints*,*/docs/*"]
    with pytest.raises(SystemExit):
        with pytest.warns(InvalidNotebookWarning):
            main([*argv, TEST_NOTEBOOK_BASE_PATH])
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


def test_run_main_use_config(capsys, tmp_path: Path):
    test_config = tmp_path / "setup.cfg"
    test_config.write_text("[flake8_nb]\nextend-ignore = E231,F401")

    argv = ["flake8_nb", "--config", test_config.resolve().as_posix()]
    with pytest.raises(SystemExit):
        with pytest.warns(InvalidNotebookWarning):
            main([*argv, TEST_NOTEBOOK_BASE_PATH])
    captured = capsys.readouterr()
    result_output = captured.out
    result_list = result_output.replace("\r", "").split("\n")
    result_list.remove("")
    expected_result_path = os.path.join(
        os.path.dirname(__file__), "data", "expected_output_config_test.txt"
    )
    with open(expected_result_path) as result_file:
        expected_result_list = result_file.readlines()
    assert len(expected_result_list) == len(result_list)
    for expected_result in expected_result_list:
        assert any(result.endswith(expected_result.rstrip("\n")) for result in result_list)


@pytest.mark.parametrize("config_file_name", ("setup.cfg", "tox.ini", ".flake8_nb"))
def test_config_discovered(
    config_file_name: str, tmp_path: Path, monkeypatch: MonkeyPatch, capsys: CaptureFixture
):
    """Check that config file is discovered."""

    test_config = tmp_path / config_file_name
    test_config.write_text("[flake8_nb]\nextend-ignore = E231,F401")

    shutil.copytree(TEST_NOTEBOOK_BASE_PATH, tmp_path / "notebooks")

    with monkeypatch.context() as m:
        m.chdir(tmp_path)
        with pytest.raises(SystemExit):
            with pytest.warns(InvalidNotebookWarning):
                main(["flake8_nb"])
    captured = capsys.readouterr()
    result_output = captured.out
    result_list = result_output.replace("\r", "").split("\n")
    result_list.remove("")
    expected_result_path = os.path.join(
        os.path.dirname(__file__), "data", "expected_output_config_test.txt"
    )
    with open(expected_result_path) as result_file:
        expected_result_list = result_file.readlines()
    assert len(expected_result_list) == len(result_list)
    for expected_result in expected_result_list:
        assert any(result.endswith(expected_result.rstrip("\n")) for result in result_list)


def test_run_main_all_excluded(capsys):
    argv = ["flake8_nb"]
    argv += [
        "--exclude",
        f"*.tox/*,*.ipynb_checkpoints*,*/docs/*,{TEST_NOTEBOOK_BASE_PATH}",
    ]
    with pytest.raises(SystemExit):
        with pytest.warns(InvalidNotebookWarning):
            main([*argv, TEST_NOTEBOOK_BASE_PATH])
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
    argv = [cli_entrypoint]
    if keep_intermediate:
        argv.append("--keep-parsed-notebooks")
    argv += ["--notebook-cell-format", notebook_cell_format]
    argv += ["--exclude", "*.tox/*,*.ipynb_checkpoints*,*/docs/*"]
    proc = subprocess.Popen(
        [*argv, TEST_NOTEBOOK_BASE_PATH], stdout=subprocess.PIPE, universal_newlines=True
    )
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


def test_flake8_nb_module_call():
    """Call flake8_nb as python module ``python -m flake8_nb --help``."""
    output = subprocess.run(
        [sys.executable, "-m", "flake8_nb", "--help"], capture_output=True, check=True
    )
    assert output.returncode == 0
    assert output.stdout.decode().startswith("usage: flake8_nb [options] file file ...")


@pytest.mark.skipif(FLAKE8_VERSION_TUPLE < (5, 0, 0), reason="Only implemented for flake8>=5.0.0")
def test_flake8_nb_bug_report():
    """Debug information."""
    output = subprocess.run(
        [sys.executable, "-m", "flake8_nb", "--bug-report"], capture_output=True, check=True
    )
    assert output.returncode == 0
    info = json.loads(output.stdout.decode())

    assert "flake8-version" in info
    assert info["flake8-version"] == flake_version
    assert info["version"] == __version__

    assert not any(plugin["plugin"] == "flake8-nb" for plugin in info["plugins"])
