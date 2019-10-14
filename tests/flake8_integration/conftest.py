# -*- coding: utf-8 -*-

import os
from typing import List, Tuple

import pytest

from ..parsers.test_notebook_parsers import TEST_NOTEBOOK_BASE_PATH

TEST_NOTEBOOK_PATHS = [
    os.path.normcase(os.path.join(TEST_NOTEBOOK_BASE_PATH, filename))
    for filename in [
        "not_a_notebook.ipynb",
        "notebook_with_flake8_tags.ipynb",
        "notebook_with_out_flake8_tags.ipynb",
        "notebook_with_out_ipython_magic.ipynb",
    ]
]


@pytest.mark.usefixtures("tmpdir")
class TempIpynbArgs:
    def __init__(self, kind: str, tmpdir_factory):
        self.kind = kind
        tmpdir = tmpdir_factory.mktemp("ipynb_folder")
        self.top_level = tmpdir.join("top_level.ipynb")
        self.top_level.write("top_level")
        self.sub_level_dir = tmpdir.mkdir("sub")
        self.sub_level = self.sub_level_dir.join("sub_level.ipynb")
        self.sub_level.write("sub_level")

    def get_args_and_result(self) -> Tuple[List[str], Tuple[List[str], List[str]]]:
        if self.kind == "file":
            return (
                [str(self.top_level), "random_arg"],
                (["random_arg"], [str(os.path.normcase(self.top_level))]),
            )
        elif self.kind == "dir":
            return (
                [str(self.sub_level_dir), "random_arg"],
                (
                    [self.sub_level_dir, "random_arg"],
                    [os.path.normcase(self.sub_level)],
                ),
            )
        elif self.kind == "random":
            return (["random_arg"], (["random_arg"], []))
        else:
            return ([], ([os.curdir], TEST_NOTEBOOK_PATHS))


@pytest.fixture(scope="session", params=["file", "dir", "random", None])
def temp_ipynb_args(request, tmpdir_factory):
    return TempIpynbArgs(request.param, tmpdir_factory)
