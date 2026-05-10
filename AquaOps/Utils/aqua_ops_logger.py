import logging
from AquaOps.Utils.singleton import singleton

@singleton
class Logger:
    def __init__(self):
        self._internal_logger = logging.getLogger("AquaOps.log")
        self._internal_logger.setLevel(logging.INFO)

    def get_logger(self):
        return self._internal_logger