# Global Configuration for Zeo++ API
# -*- coding: utf-8 -*-
# Author: Shibo Li
# Date: 2025-05-13

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file if present
load_dotenv()

# Workspace base directory
WORKSPACE_ROOT = Path(os.getenv("ZEO_WORKSPACE", "workspace"))
TMP_DIR = WORKSPACE_ROOT / "tmp"
CACHE_DIR = WORKSPACE_ROOT / "cache"

# Zeo++ executable path
ZEO_EXECUTABLE = os.getenv("ZEO_EXEC_PATH", "./network")

# Runtime settings
ENABLE_CACHE = os.getenv("ENABLE_CACHE", "true").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
