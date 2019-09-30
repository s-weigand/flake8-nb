from . import __version__

from flake8.main.application import Application


class Flake8NbApplication(Application):
    def __init__(self, program="flake8_nb", version=__version__):
        super().__init__(self, program, version)
