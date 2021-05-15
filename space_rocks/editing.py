from typing import Callable

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from space_rocks import constants


class _FileHandler(FileSystemEventHandler):
    def __init__(self, on_change: Callable[[], None]):
        super(_FileHandler, self).__init__()
        self._restart_level = on_change

    def on_modified(self, event: FileSystemEvent):
        if event.is_directory:
            return
        if event.src_path.endswith(
            "~"
        ):  # seems pycharm gens these temp files, so ignore them
            return
        self._restart_level()


class LevelObserver:
    def __init__(self, on_change: Callable[[], None]):
        event_handler = _FileHandler(on_change)
        observer = Observer()
        observer.schedule(event_handler, constants.LEVELS_ROOT, recursive=True)
        observer.start()
