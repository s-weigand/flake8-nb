"""Test file for the precommit hook."""
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent


def test_hook_output():
    """Tests that flake8-nb output is contained in the hooks output."""
    flake8_nb_output_lines = (REPO_ROOT / "flake8-nb_run_output.txt").read_text().splitlines()
    hook_output_lines = (REPO_ROOT / "hook_run_output.txt").read_text().splitlines()
    # the first line is removed due to different location of the executable
    flake8_nb_output_lines = flake8_nb_output_lines[1:]
    assert all(
        flake8_nb_output_line in hook_output_lines
        for flake8_nb_output_line in flake8_nb_output_lines
    )
