from watchdog.events import FileSystemEventHandler
from typing import Callable

class FileHandler(FileSystemEventHandler):
    def __init__(self, restart_level : Callable):
        super(FileHandler, self).__init__()
        self._restart_level = restart_level

    def on_modified(self, event):

        if event.is_directory:
            return

        if event.src_path.endswith("~"): # seems pycharm gens these temp files, so ignore them
            return

        l = self._restart_level()
        print("")
