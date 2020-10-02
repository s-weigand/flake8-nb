# flake8-nb

[![PyPi Version](https://img.shields.io/pypi/v/flake8_nb.svg)](https://pypi.org/project/flake8-nb/)
[![Conda Version](https://img.shields.io/conda/vn/conda-forge/flake8-nb.svg)](https://anaconda.org/conda-forge/flake8-nb)
[![Supported Python Versions](https://img.shields.io/pypi/pyversions/flake8_nb.svg)](https://pypi.org/project/flake8-nb/)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

[![Actions Status](https://github.com/s-weigand/flake8-nb/workflows/Tests/badge.svg)](https://github.com/s-weigand/flake8-nb/actions)
[![Documentation Status](https://readthedocs.org/projects/flake8-nb/badge/?version=latest)](https://flake8-nb.readthedocs.io/en/latest/?badge=latest)
[![Testing Coverage](https://codecov.io/gh/s-weigand/flake8-nb/branch/master/graph/badge.svg)](https://codecov.io/gh/s-weigand/flake8-nb)
[![Documentation Coverage](https://flake8-nb.readthedocs.io/en/latest/_static/interrogate_badge.svg)](https://github.com/s-weigand/flake8-nb)
[![Dependabot Status](https://api.dependabot.com/badges/status?host=github&repo=s-weigand/flake8-nb)](https://dependabot.com)

[![Code quality](https://api.codacy.com/project/badge/Grade/d02b436a637243a1b626b74d018c3bbe)](https://www.codacy.com/manual/s.weigand.phy/flake8-nb?utm_source=github.com&utm_medium=referral&utm_content=s-weigand/flake8-nb&utm_campaign=Badge_Grade)
[![All Contributors](https://img.shields.io/github/all-contributors/s-weigand/flake8-nb)](#contributors)
[![Code style Python: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Binder](https://static.mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/s-weigand/flake8-nb.git/master?urlpath=lab%2Ftree%2Ftests%2Fdata%2Fnotebooks)

[`flake8`](https://gitlab.com/pycqa/flake8) checking for jupyter notebooks.
Basically this is a hack on the `flake8`'s `Application` class,
which adds parsing and a cell based formatter for `*.ipynb` files.

## Features

- flake8 CLI tests for jupyter notebooks
- Full base functionality of `flake8` and its plugins
- Input cell based error formatting
- Report fine tuning with cell-tags (`flake8-noqa-tags` see [usage](https://flake8-nb.readthedocs.io/en/latest/usage.html#cell-tags))

## Example

If you had a notebook with name `example_notebook.ipynb`, where the code cell
which was executed as 34th cell (`In[34]`) had the following code:

```python
bad_formated_dict = {"missing":"space"}
```

running `flake8_nb` would result in the following output.

```bash
$ flake8_nb example_notebook.ipynb
example_notebook.ipynb#In[34]:1:31: E231 missing whitespace after ':'
```

## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tr>
    <td align="center"><a href="https://github.com/s-weigand"><img src="https://avatars2.githubusercontent.com/u/9513634?v=4" width="100px;" alt=""/><br /><sub><b>Sebastian Weigand</b></sub></a><br /><a href="https://github.com/s-weigand/flake8-nb/commits?author=s-weigand" title="Code">💻</a> <a href="#ideas-s-weigand" title="Ideas, Planning, & Feedback">🤔</a> <a href="#maintenance-s-weigand" title="Maintenance">🚧</a> <a href="#projectManagement-s-weigand" title="Project Management">📆</a> <a href="#infra-s-weigand" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a> <a href="https://github.com/s-weigand/flake8-nb/commits?author=s-weigand" title="Tests">⚠️</a> <a href="https://github.com/s-weigand/flake8-nb/commits?author=s-weigand" title="Documentation">📖</a></td>
    <td align="center"><a href="https://jtmiclat.me"><img src="https://avatars0.githubusercontent.com/u/30991698?v=4" width="100px;" alt=""/><br /><sub><b>Jt Miclat</b></sub></a><br /><a href="https://github.com/s-weigand/flake8-nb/issues?q=author%3Ajtmiclat" title="Bug reports">🐛</a></td>
    <td align="center"><a href="http://eisenhauer.io"><img src="https://avatars3.githubusercontent.com/u/3607591?v=4" width="100px;" alt=""/><br /><sub><b>Philipp Eisenhauer</b></sub></a><br /><a href="https://github.com/s-weigand/flake8-nb/issues?q=author%3Apeisenha" title="Bug reports">🐛</a></td>
    <td align="center"><a href="https://shmokmt.github.io/"><img src="https://avatars1.githubusercontent.com/u/32533860?v=4" width="100px;" alt=""/><br /><sub><b>Shoma Okamoto</b></sub></a><br /><a href="https://github.com/s-weigand/flake8-nb/commits?author=shmokmt" title="Tests">⚠️</a></td>
    <td align="center"><a href="https://marcogorelli.github.io/"><img src="https://avatars2.githubusercontent.com/u/33491632?v=4" width="100px;" alt=""/><br /><sub><b>Marco Gorelli</b></sub></a><br /><a href="#tool-MarcoGorelli" title="Tools">🔧</a> <a href="https://github.com/s-weigand/flake8-nb/commits?author=MarcoGorelli" title="Documentation">📖</a></td>
  </tr>
</table>

<!-- markdownlint-enable -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!
