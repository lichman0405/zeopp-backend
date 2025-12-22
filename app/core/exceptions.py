# Custom Exceptions for Zeo++ API
# -*- coding: utf-8 -*-
# Author: Shibo Li
# Date: 2025-12-22
# Version: 0.3.0

"""
Custom exception classes for better error handling and debugging.
"""

class ZeoppBaseException(Exception):
    """Base exception for all Zeo++ API errors."""
    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ZeoppExecutionError(ZeoppBaseException):
    """Raised when Zeo++ command execution fails."""
    def __init__(self, message: str, exit_code: int = None, stderr: str = None):
        details = {
            "exit_code": exit_code,
            "stderr": stderr
        }
        super().__init__(message, details)
        self.exit_code = exit_code
        self.stderr = stderr


class ZeoppParsingError(ZeoppBaseException):
    """Raised when parsing Zeo++ output fails."""
    def __init__(self, message: str, output_file: str = None, raw_content: str = None):
        details = {
            "output_file": output_file,
            "raw_content": raw_content[:200] if raw_content else None  # Truncate for logging
        }
        super().__init__(message, details)
        self.output_file = output_file
        self.raw_content = raw_content


class ZeoppOutputNotFoundError(ZeoppBaseException):
    """Raised when expected output file is not generated."""
    def __init__(self, message: str, expected_file: str = None):
        details = {"expected_file": expected_file}
        super().__init__(message, details)
        self.expected_file = expected_file


class ZeoppValidationError(ZeoppBaseException):
    """Raised when input validation fails."""
    def __init__(self, message: str, field: str = None, value: any = None):
        details = {
            "field": field,
            "value": str(value) if value is not None else None
        }
        super().__init__(message, details)
        self.field = field
        self.value = value
