from __future__ import annotations

import logging
import os
from pathlib import Path


def configure_logging(level: int = logging.INFO) -> None:
    '''
    Configure root logging for the application.

    This function is intentionally idempotent enough for startup use:
    existing handlers are cleared before new ones are attached.
    '''
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()

    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    log_dir = os.environ.get('ASTRAL_LOG_DIR')
    if log_dir:
        file_handler = logging.FileHandler(
            Path(log_dir) / 'astralengine.log',
            encoding='utf-8',
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    logging.getLogger(__name__).debug('Logging configured.')