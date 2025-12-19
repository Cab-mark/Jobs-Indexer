from __future__ import annotations

import logging
import sys
from typing import Any, Dict

from pythonjsonlogger import jsonlogger


def setup_logger(level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger("jobs-indexer")
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = jsonlogger.JsonFormatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s %(extra)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(level.upper())
    logger.propagate = False
    return logger


def log_extra(**kwargs: Any) -> Dict[str, Any]:
    return {"extra": kwargs}
