from __future__ import annotations

import logging
from logging import Logger
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path


_LOGGER_NAME = 'astralengine'


def configure_logging(
        level: int = logging.INFO,
        log_dir: str | Path = 'logs',
        log_filename: str = 'astralengine.log',
        console: bool = True,
        file_output: bool = True,
        debug: bool = False
    ) -> Logger:
    '''
    Configure root logging for the application and return it.

    Can be called multiple times without duplicating log lines.
    '''
    root_logger = logging.getLogger(_LOGGER_NAME)
    root_logger.setLevel(level)
    root_logger.propagate = False

    root_logger.handlers.clear()

    formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    if console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    if file_output:
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            log_path / log_filename,
            maxBytes=5_000_000,
            backupCount=3,
            encoding='utf-8',
            mode='w' if debug else 'a'
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    root_logger.debug('Logging configuration')
    return root_logger

def get_logger(name: str | None = None) -> Logger:
    '''
    Returns the engine logger or specified child logger.
    '''
    base = logging.getLogger(_LOGGER_NAME)
    
    if name is None:
        return base
    
    return base.getChild(name)