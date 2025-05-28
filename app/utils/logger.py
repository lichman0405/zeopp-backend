# Rich Logger for Zeo++ API
# -*- coding: utf-8 -*-
# Author: Shibo Li
# Date: 2025-05-13

import logging
from rich.logging import RichHandler
from app.core.config import LOG_LEVEL


def get_logger(name: str = "zeopp-api") -> logging.Logger:
    logging.basicConfig(
        level=LOG_LEVEL,
        format="%(message)s",
        handlers=[RichHandler(rich_tracebacks=True)]
    )
    return logging.getLogger(name)


logger = get_logger()
