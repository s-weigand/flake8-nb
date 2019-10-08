from typing import List, Tuple, Union

import pytest


@pytest.mark.usefixtures("tmpdir")
class TempIpynbArgs:
    def __init__(self, kind: str, tmpdir_factory):
        self.kind = kind
        tmpdir = tmpdir_factory.mktemp("ipynb_folder")
        self.top_level = tmpdir.join("top_level.ipynb")
        self.top_level.write("top_level")
        self.sub_level_dir = tmpdir.mkdir("sub")
        sub_level = self.sub_level_dir.join("sub_level.ipynb")
        sub_level.write("sub_level")

    def get_args_and_result(self) -> Tuple[List[str], Union[bool, None]]:
        if self.kind == "file":
            return ([str(self.top_level), "random_arg"], True)
        elif self.kind == "dir":
            return ([str(self.sub_level_dir), "random_arg"], True)
        elif self.kind == "random":
            return (["random_arg"], False)
        else:
            return ([], True)


@pytest.fixture(scope="session", params=["file", "dir", "random", ""])
def temp_ipynb_args(request, tmpdir_factory):
    return TempIpynbArgs(request.param, tmpdir_factory)


# def test_create_file(tmpdir):
#     p = tmpdir.mkdir("sub").join("hello.txt")
#     p.write("content")
#     assert p.read() == "content"
#     assert len(tmpdir.listdir()) == 1
#     assert 0
