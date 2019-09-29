#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = ["flake8>=3.0.0"]


setup_requirements = ["pytest-runner"]

test_requirements = ["pytest>=3"]

setup(
    author="Sebastian Weigand",
    author_email="s.weigand.phy@gmail.com",
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Framework :: Flake8",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Quality Assurance",
    ],
    description="Flake8 extension to check notebooks",
    install_requires=requirements,
    entry_points={"flake8.extension": ["IPYNB1 = flake8_nb:Flake8Notebook"]},
    long_description=readme + "\n\n" + history,
    long_description_content_type="text/x-rst",
    license="Apache Software License 2.0",
    include_package_data=True,
    keywords="flake8_nb flake8 lint quotes notebook jupyter ipython",
    name="flake8_nb",
    packages=find_packages(include=["flake8_nb", "flake8_nb.*"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/s-weigand/flake8_nb",
    version="0.1.0",
    zip_safe=False,
)
