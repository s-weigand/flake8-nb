# -*- coding: utf-8 -*-
import os
from typing import Iterator

import pytest

from flake8_nb.parsers.notebook_parsers import InvalidNotebookWarning, NotebookParser

from .parsers.test_notebook_parsers import TEST_NOTEBOOK_BASE_PATH


@pytest.fixture(scope="function")
def notebook_parser() -> Iterator[NotebookParser]:
    notebooks = [
        "not_a_notebook.ipynb",
        "notebook_with_flake8_tags.ipynb",
        "notebook_with_out_flake8_tags.ipynb",
        "notebook_with_out_ipython_magic.ipynb",
    ]
    notebook_paths = [
        os.path.join(TEST_NOTEBOOK_BASE_PATH, notebook) for notebook in notebooks
    ]
    with pytest.warns(InvalidNotebookWarning):
        parser_instance = NotebookParser(notebook_paths)
    yield parser_instance
    parser_instance.clean_up()
