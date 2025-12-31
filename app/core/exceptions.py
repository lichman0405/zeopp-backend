# Custom Exceptions for Zeo++ API
# -*- coding: utf-8 -*-
# Author: Shibo Li
# Date: 2025-12-22
# Updated: 2025-12-31 - Added error codes and standardized error response
# Version: 0.3.1

"""
Custom exception classes for better error handling and debugging.
Provides standardized error codes and response formats.
"""

from enum import Enum
from typing import Optional, Any
from pydantic import BaseModel


class ErrorCode(str, Enum):
    """Standardized error codes for API responses."""
    # Execution errors (1xxx)
    EXECUTION_FAILED = "ZEOPP_1001"
    TIMEOUT = "ZEOPP_1002"
    
    # Parsing errors (2xxx)
    PARSING_FAILED = "ZEOPP_2001"
    OUTPUT_NOT_FOUND = "ZEOPP_2002"
    INVALID_FORMAT = "ZEOPP_2003"
    
    # Validation errors (3xxx)
    INVALID_FILE_TYPE = "ZEOPP_3001"
    FILE_TOO_LARGE = "ZEOPP_3002"
    INVALID_PARAMETER = "ZEOPP_3003"
    
    # System errors (4xxx)
    INTERNAL_ERROR = "ZEOPP_4001"
    CACHE_ERROR = "ZEOPP_4002"


class ErrorResponse(BaseModel):
    """Standardized error response model."""
    success: bool = False
    error_code: str
    message: str
    details: Optional[dict] = None
    request_id: Optional[str] = None


class ZeoppBaseException(Exception):
    """Base exception for all Zeo++ API errors."""
    error_code: ErrorCode = ErrorCode.INTERNAL_ERROR
    
    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)
    
    def to_response(self, request_id: str = None) -> ErrorResponse:
        """Convert exception to standardized error response."""
        return ErrorResponse(
            error_code=self.error_code.value,
            message=self.message,
            details=self.details,
            request_id=request_id
        )


class ZeoppExecutionError(ZeoppBaseException):
    """Raised when Zeo++ command execution fails."""
    error_code = ErrorCode.EXECUTION_FAILED
    
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
    error_code = ErrorCode.PARSING_FAILED
    
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
    error_code = ErrorCode.OUTPUT_NOT_FOUND
    
    def __init__(self, message: str, expected_file: str = None):
        details = {"expected_file": expected_file}
        super().__init__(message, details)
        self.expected_file = expected_file


class ZeoppValidationError(ZeoppBaseException):
    """Raised when input validation fails."""
    error_code = ErrorCode.INVALID_PARAMETER
    
    def __init__(self, message: str, field: str = None, value: Any = None):
        details = {
            "field": field,
            "value": str(value) if value is not None else None
        }
        super().__init__(message, details)
        self.field = field
        self.value = value


class ZeoppFileTooLargeError(ZeoppBaseException):
    """Raised when uploaded file exceeds size limit."""
    error_code = ErrorCode.FILE_TOO_LARGE
    
    def __init__(self, message: str, file_size: int = None, max_size: int = None):
        details = {
            "file_size_bytes": file_size,
            "max_size_bytes": max_size
        }
        super().__init__(message, details)


class ZeoppInvalidFileTypeError(ZeoppBaseException):
    """Raised when uploaded file has invalid extension."""
    error_code = ErrorCode.INVALID_FILE_TYPE
    
    def __init__(self, message: str, filename: str = None, allowed_types: list = None):
        details = {
            "filename": filename,
            "allowed_types": allowed_types
        }
        super().__init__(message, details)
