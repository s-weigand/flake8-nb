# History

## 0.2.4 (2020-10-04)

- Set max supported version of `flake8` to be `<3.8.5`

## 0.2.3 (2020-10-02)

- Fixed pre-commit hook file association so it support python and juypter notebooks

## 0.2.1 (2020-08-11)

- Forced uft8 encoding when reading notebooks,
  this prevents errors on windows when console codepage is assumed

## 0.2.0 (2020-07-18)

- Added pre-commit hook ([#47](https://github.com/s-weigand/flake8-nb/pull/47))

## 0.1.8 (2020-06-09)

- Set max supported version of `flake8` to be `<=3.8.3`

## 0.1.7 (2020-05-25)

- Set max supported version of `flake8` to be `<=3.8.2`

## 0.1.6 (2020-05-20)

- Set max supported version of `flake8` to be `<=3.8.1`
- Fixed bug with `--exclude` option

## 0.1.4 (2020-01-01)

- Set max supported version of `flake8` to be `<3.8.0`, to prevent breaking due to changes of `flake8`'s inner workings.

## 0.1.3 (2019-11-13)

- Added official Python 3.8 support and tests

## 0.1.2 (2019-10-29)

- Fixed compatibility with `flake8==3.7.9`

## 0.1.1 (2019-10-24)

- Added console-script 'flake8-nb' as an alias for 'flake8_nb'

## 0.1.0 (2019-10-22)

- First release on PyPI.
