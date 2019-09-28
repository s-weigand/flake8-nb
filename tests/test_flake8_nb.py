#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `flake8_nb` package."""

# import pytest


from flake8_nb.flake8_nb import strip_newline, add_newline, generate_input_name


def test_strip_newline():
    assert strip_newline("test string\n") == "test string"


def test_add_newline():
    assert add_newline("test string") == "test string\n"


def test_generate_input_name():
    assert generate_input_name("test_notebook.ipynb", 1) == "test_notebook.ipynb#In[1]"
