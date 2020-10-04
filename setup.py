#!/usr/bin/env python

"""The setup script."""

import os
import sys

from setuptools import find_packages
from setuptools import setup

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "flake8_nb"))

with open("README.md", encoding="utf-8") as readme_file:
    readme = readme_file.read()

with open("HISTORY.md", encoding="utf-8") as history_file:
    history = history_file.read()

requirements = ["flake8>=3.7.0,<3.8.5", "nbconvert>=5.6.0", "ipython>=7.8.0"]

# This is a hack to test against the flake8 master branch
tox_env_name = os.environ.get("TOX_ENV_NAME", None)
if tox_env_name and tox_env_name == "flake8-nightly":
    requirements[0] = "flake8>=3.0.0"

setup_requirements = ["pytest-runner"]

test_requirements = ["pytest>=3"]

setup(
    author="Sebastian Weigand",
    author_email="s.weigand.phy@gmail.com",
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Framework :: Jupyter",
        "Framework :: Flake8",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Quality Assurance",
    ],
    project_urls={
        "Documentation": "https://flake8-nb.readthedocs.io/en/latest/",
        "Source": "https://github.com/s-weigand/flake8-nb",
        "Tracker": "https://github.com/s-weigand/flake8-nb/issues",
    },
    description="Flake8 based checking for jupyter notebooks",
    install_requires=requirements,
    long_description=readme + "\n\n" + history,
    long_description_content_type="text/markdown",
    license="Apache Software License 2.0",
    include_package_data=True,
    keywords="flake8_nb flake8 lint notebook jupyter ipython",
    name="flake8_nb",
    packages=find_packages(include=["flake8_nb", "flake8_nb.*"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    platforms="any",
    entry_points={
        "console_scripts": [
            "flake8_nb = flake8_nb.__main__:main",
            "flake8-nb = flake8_nb.__main__:main",
        ],
        "flake8.report": "default_notebook = flake8_nb:IpynbFormatter",
    },
    tests_require=test_requirements,
    url="https://github.com/s-weigand/flake8-nb",
    version="0.2.4",
    zip_safe=False,
)
