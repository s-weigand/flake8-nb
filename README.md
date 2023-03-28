# flake8-nb

[![PyPi Version](https://img.shields.io/pypi/v/flake8_nb.svg)](https://pypi.org/project/flake8-nb/)
[![Conda Version](https://img.shields.io/conda/vn/conda-forge/flake8-nb.svg)](https://anaconda.org/conda-forge/flake8-nb)
[![Supported Python Versions](https://img.shields.io/pypi/pyversions/flake8_nb.svg)](https://pypi.org/project/flake8-nb/)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

[![Actions Status](https://github.com/s-weigand/flake8-nb/workflows/Tests/badge.svg)](https://github.com/s-weigand/flake8-nb/actions)
[![Documentation Status](https://readthedocs.org/projects/flake8-nb/badge/?version=latest)](https://flake8-nb.readthedocs.io/en/latest/?badge=latest)
[![Testing Coverage](https://codecov.io/gh/s-weigand/flake8-nb/branch/main/graph/badge.svg)](https://codecov.io/gh/s-weigand/flake8-nb)
[![Documentation Coverage](https://flake8-nb.readthedocs.io/en/latest/_static/interrogate_badge.svg)](https://github.com/s-weigand/flake8-nb)

[![Codacy Badge](https://app.codacy.com/project/badge/Grade/d02b436a637243a1b626b74d018c3bbe)](https://www.codacy.com/gh/s-weigand/flake8-nb/dashboard?utm_source=github.com&utm_medium=referral&utm_content=s-weigand/flake8-nb&utm_campaign=Badge_Grade)
[![All Contributors](https://img.shields.io/github/all-contributors/s-weigand/flake8-nb)](#contributors)
[![Code style Python: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Binder](https://static.mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/s-weigand/flake8-nb.git/main?urlpath=lab%2Ftree%2Ftests%2Fdata%2Fnotebooks)

[`flake8`](https://github.com/pycqa/flake8) checking for jupyter notebooks.

This tool is mainly aimed towards writing tutorials/lecture material, where one might also want
to show off bad practices and/or errors, while still keeping the rest of the code clean and
without adding the complexity of tooling to the readers
(see [docs on cell tags](https://flake8-nb.readthedocs.io/en/latest/usage.html#cell-tags)).

Basically this is a hack on the `flake8`'s `Application` class,
which adds parsing and a cell based formatter for `*.ipynb` files.

This is **NOT A PLUGIN** but a stand alone CLI tool/[pre-commit](https://pre-commit.com/) hook to be used instead of the `flake8` command/hook.

## Features

- flake8 CLI tests for jupyter notebooks
- Full base functionality of `flake8` and its plugins
- Input cell based error formatting (Execution count/code cell count/total cellcount)
- Report fine tuning with cell-tags (`flake8-noqa-tags` see [usage](https://flake8-nb.readthedocs.io/en/latest/usage.html#cell-tags))
- [pre-commit](https://pre-commit.com/) hook

## Examples

## Default reporting

If you had a notebook with name `example_notebook.ipynb`, where the code cell
which was executed as 34th cell (`In[34]`) had the following code:

```python
bad_formatted_dict = {"missing":"space"}
```

running `flake8_nb` would result in the following output.

### Execution count

```bash
$ flake8_nb example_notebook.ipynb
example_notebook.ipynb#In[34]:1:31: E231 missing whitespace after ':'
```

## Custom reporting

If you prefer the reports to show the cell number rather then the execution count you
can use the `--notebook-cell-format` option, given that the cell is the 5th `code` cell
and 10th total cell (taking `raw` and `markdown` cells into account),
you will get the following output.

### Code cell count

```bash
$ flake8_nb --notebook-cell-format '{nb_path}:code_cell#{code_cell_count}' example_notebook.ipynb
example_notebook.ipynb:code_cell#5:1:31: E231 missing whitespace after ':'
```

### Total cell count

```bash
$ flake8_nb --notebook-cell-format '{nb_path}:cell#{total_cell_count}' example_notebook.ipynb
example_notebook.ipynb:cell#10:1:31: E231 missing whitespace after ':'
```

## Similar projects

- [nbQA](https://github.com/nbQA-dev/nbQA):
  Run isort, pyupgrade, mypy, pylint, flake8, mdformat, black, blacken-docs, and more on Jupyter Notebooks

## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/s-weigand"><img src="https://avatars2.githubusercontent.com/u/9513634?v=4?s=100" width="100px;" alt="Sebastian Weigand"/><br /><sub><b>Sebastian Weigand</b></sub></a><br /><a href="https://github.com/s-weigand/flake8-nb/commits?author=s-weigand" title="Code">💻</a> <a href="#ideas-s-weigand" title="Ideas, Planning, & Feedback">🤔</a> <a href="#maintenance-s-weigand" title="Maintenance">🚧</a> <a href="#projectManagement-s-weigand" title="Project Management">📆</a> <a href="#infra-s-weigand" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a> <a href="https://github.com/s-weigand/flake8-nb/commits?author=s-weigand" title="Tests">⚠️</a> <a href="https://github.com/s-weigand/flake8-nb/commits?author=s-weigand" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://jtmiclat.me"><img src="https://avatars0.githubusercontent.com/u/30991698?v=4?s=100" width="100px;" alt="Jt Miclat"/><br /><sub><b>Jt Miclat</b></sub></a><br /><a href="https://github.com/s-weigand/flake8-nb/issues?q=author%3Ajtmiclat" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://eisenhauer.io"><img src="https://avatars3.githubusercontent.com/u/3607591?v=4?s=100" width="100px;" alt="Philipp Eisenhauer"/><br /><sub><b>Philipp Eisenhauer</b></sub></a><br /><a href="https://github.com/s-weigand/flake8-nb/issues?q=author%3Apeisenha" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://shmokmt.github.io/"><img src="https://avatars1.githubusercontent.com/u/32533860?v=4?s=100" width="100px;" alt="Shoma Okamoto"/><br /><sub><b>Shoma Okamoto</b></sub></a><br /><a href="https://github.com/s-weigand/flake8-nb/commits?author=shmokmt" title="Tests">⚠️</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://marcogorelli.github.io/"><img src="https://avatars2.githubusercontent.com/u/33491632?v=4?s=100" width="100px;" alt="Marco Gorelli"/><br /><sub><b>Marco Gorelli</b></sub></a><br /><a href="#tool-MarcoGorelli" title="Tools">🔧</a> <a href="https://github.com/s-weigand/flake8-nb/commits?author=MarcoGorelli" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://blog.ouseful.info"><img src="https://avatars.githubusercontent.com/u/82988?v=4?s=100" width="100px;" alt="Tony Hirst"/><br /><sub><b>Tony Hirst</b></sub></a><br /><a href="#ideas-psychemedia" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Dobatymo"><img src="https://avatars.githubusercontent.com/u/7647594?v=4?s=100" width="100px;" alt="Dobatymo"/><br /><sub><b>Dobatymo</b></sub></a><br /><a href="https://github.com/s-weigand/flake8-nb/issues?q=author%3ADobatymo" title="Bug reports">🐛</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/AlpAribal"><img src="https://avatars.githubusercontent.com/u/6286038?v=4?s=100" width="100px;" alt="Alp Arıbal"/><br /><sub><b>Alp Arıbal</b></sub></a><br /><a href="https://github.com/s-weigand/flake8-nb/issues?q=author%3AAlpAribal" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://www.tuhh.de/mls/en/institute/associates/marvin-kastner-msc.html"><img src="https://avatars.githubusercontent.com/u/5236165?v=4?s=100" width="100px;" alt="1kastner"/><br /><sub><b>1kastner</b></sub></a><br /><a href="https://github.com/s-weigand/flake8-nb/issues?q=author%3A1kastner" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/dominiquesydow"><img src="https://avatars.githubusercontent.com/u/7207093?v=4?s=100" width="100px;" alt="Dominique Sydow"/><br /><sub><b>Dominique Sydow</b></sub></a><br /><a href="https://github.com/s-weigand/flake8-nb/issues?q=author%3Adominiquesydow" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://www.keegan.ch"><img src="https://avatars.githubusercontent.com/u/12845624?v=4?s=100" width="100px;" alt="Liam Keegan"/><br /><sub><b>Liam Keegan</b></sub></a><br /><a href="https://github.com/s-weigand/flake8-nb/issues?q=author%3Alkeegan" title="Bug reports">🐛</a> <a href="https://github.com/s-weigand/flake8-nb/commits?author=lkeegan" title="Code">💻</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!
