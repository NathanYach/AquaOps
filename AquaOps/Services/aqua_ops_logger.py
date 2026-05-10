import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from AquaOps.Services.singleton import singleton


@singleton
class Logger:
    def __init__(self):
        self._internal_logger = logging.getLogger("AquaOps")
        self._internal_logger.setLevel(logging.INFO)

        # Prevent duplicate handlers if singleton reloads
        if not self._internal_logger.handlers:

            log_path = Path("AquaOps.log")

            file_handler = logging.FileHandler(log_path)

            formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(message)s"
            )

            file_handler.setFormatter(formatter)

            self._internal_logger.addHandler(file_handler)

    def get_logger(self):
        return self._internal_logger