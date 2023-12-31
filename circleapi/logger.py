import logging
import queue
from logging.handlers import QueueHandler, QueueListener
from contextlib import contextmanager
from threading import Thread


logger = logging.getLogger("circleapi")
if not logger.hasHandlers():
    logger.addHandler(logging.NullHandler())


def setup_logging_queue(to_console=False, to_file: str | None = None) -> QueueListener:
    log_queue = queue.Queue(-1)
    queue_handler = QueueHandler(log_queue)

    formatter = logging.Formatter("%(asctime)s [%(name)s][%(threadName)s][%(levelname)s] %(message)s")
    log = logging.getLogger("circleapi")
    log.setLevel(logging.DEBUG)
    log.addHandler(queue_handler)

    handlers = []
    if to_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        handlers.append(console_handler)

    if to_file:
        file_handler = logging.FileHandler(to_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)

    if not handlers:
        raise NotImplementedError

    listener = QueueListener(log_queue, *handlers)
    return listener


@contextmanager
def start_logging(to_console=False, to_file: str | None = None) -> Thread:
    log = setup_logging_queue(to_console, to_file)
    log.start()
    try:
        yield log
    finally:
        log.stop()
