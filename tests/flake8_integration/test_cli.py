from .conftest import TempIpynbArgs


from flake8_nb.flake8_integration.cli import get_notebooks_from_args


def test_get_notebooks_from_args(temp_ipynb_args: TempIpynbArgs):
    args, expected_result = temp_ipynb_args.get_args_and_result()
    assert (len(get_notebooks_from_args(args)) != 0) == expected_result
