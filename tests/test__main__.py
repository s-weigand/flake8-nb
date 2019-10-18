# -*- coding: utf-8 -*-

import os
import re
import subprocess

import pytest

from flake8_nb.__main__ import main
from flake8_nb.parsers.notebook_parsers import InvalidNotebookWarning, NotebookParser

from .parsers.test_notebook_parsers import TEST_NOTEBOOK_BASE_PATH


@pytest.mark.parametrize("keep_intermediate", [True, False])
def test_integration_system_call(keep_intermediate: bool):
    argv = ["flake8_nb", TEST_NOTEBOOK_BASE_PATH]
    if keep_intermediate:
        argv.append("--keep-parsed-notebooks")
    process = subprocess.Popen(
        argv, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout_value, stderr_value = process.communicate()
    result_list = stdout_value.replace(b"\r", b"").split(b"\n")
    expected_result_path = os.path.join(
        os.path.dirname(__file__), "data", "expected_output.txt"
    )
    with open(expected_result_path, "rb") as result_file:
        expected_result_list = result_file.readlines()
    for result, expected_result in zip(result_list, expected_result_list):
        assert result.endswith(expected_result.rstrip(b"\n"))

    if keep_intermediate:
        temp_path = re.search(rb"present at:\s+(.+?)\s+", stderr_value, re.DOTALL)
        assert os.path.exists(temp_path.group(1))
        NotebookParser.temp_path = temp_path.group(1)
        NotebookParser.clean_up()


@pytest.mark.parametrize("keep_intermediate", [True, False])
def test_run_main(capsys, keep_intermediate: bool):
    argv = ["flake8_nb", TEST_NOTEBOOK_BASE_PATH]
    if keep_intermediate:
        argv.append("--keep-parsed-notebooks")
    try:
        with pytest.warns(InvalidNotebookWarning):
            main(argv)
    except SystemExit:
        pass
    captured = capsys.readouterr()
    result_output = captured.out
    result_list = result_output.replace("\r", "").split("\n")
    expected_result_path = os.path.join(
        os.path.dirname(__file__), "data", "expected_output.txt"
    )
    with open(expected_result_path, "r") as result_file:
        expected_result_list = result_file.readlines()
    for result, expected_result in zip(result_list, expected_result_list):
        assert result.endswith(expected_result.rstrip("\n"))

    if keep_intermediate:
        assert os.path.exists(NotebookParser.temp_path)
        NotebookParser.clean_up()
