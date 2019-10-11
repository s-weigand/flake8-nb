from .conftest import TempIpynbArgs


from flake8_nb.flake8_integration.cli import get_notebooks_from_args


def test_get_notebooks_from_args(temp_ipynb_args: TempIpynbArgs):
    orig_args, (expected_args, expected_nb_list) = temp_ipynb_args.get_args_and_result()
    args, nb_list = get_notebooks_from_args(orig_args)
    assert sorted(args) == sorted(expected_args)
    assert sorted(nb_list) == sorted(expected_nb_list)
