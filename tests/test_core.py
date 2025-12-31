# Unit Tests for Core Utilities
# -*- coding: utf-8 -*-
# Author: Shibo Li
# Date: 2025-12-31

import pytest

from app.core.config import Settings
from app.core.exceptions import (
    ZeoppError,
    ZeoppExecutionError,
    ZeoppParsingError,
    ZeoppTimeoutError,
    FileValidationError,
    ErrorCode,
)
from app.core.middleware import validate_structure_file, ALLOWED_EXTENSIONS


class TestSettings:
    """Test cases for application settings."""

    def test_default_settings(self):
        """Test default settings values."""
        settings = Settings()
        assert settings.app_name == "Zeo++ Backend API"
        assert settings.version == "0.3.1"
        assert settings.enable_cache is True

    def test_settings_from_env(self, monkeypatch):
        """Test settings loaded from environment variables."""
        monkeypatch.setenv("ENABLE_CACHE", "false")
        monkeypatch.setenv("MAX_UPLOAD_SIZE_MB", "100")
        
        settings = Settings()
        assert settings.enable_cache is False
        assert settings.max_upload_size_mb == 100

    def test_cors_origins_parsing(self):
        """Test CORS origins configuration."""
        settings = Settings()
        assert isinstance(settings.cors_origins, list)


class TestExceptions:
    """Test cases for custom exceptions."""

    def test_zeopp_error_base(self):
        """Test base ZeoppError exception."""
        error = ZeoppError("Test error")
        assert str(error) == "Test error"
        assert error.error_code == ErrorCode.INTERNAL_ERROR

    def test_zeopp_execution_error(self):
        """Test ZeoppExecutionError with additional attributes."""
        error = ZeoppExecutionError(
            message="Execution failed",
            command="network -res test.cif",
            return_code=1,
            stderr="Error output"
        )
        assert error.error_code == ErrorCode.EXECUTION_ERROR
        assert error.command == "network -res test.cif"
        assert error.return_code == 1
        assert error.stderr == "Error output"

    def test_zeopp_parsing_error(self):
        """Test ZeoppParsingError with file context."""
        error = ZeoppParsingError(
            message="Parse failed",
            output_file="result.res",
            raw_content="invalid content"
        )
        assert error.error_code == ErrorCode.PARSE_ERROR
        assert error.output_file == "result.res"
        assert error.raw_content == "invalid content"

    def test_zeopp_timeout_error(self):
        """Test ZeoppTimeoutError with timeout value."""
        error = ZeoppTimeoutError(
            message="Timed out",
            timeout_seconds=60
        )
        assert error.error_code == ErrorCode.TIMEOUT_ERROR
        assert error.timeout_seconds == 60

    def test_file_validation_error(self):
        """Test FileValidationError with file details."""
        error = FileValidationError(
            message="Invalid file",
            filename="test.xyz",
            allowed_extensions=[".cif", ".cssr"]
        )
        assert error.error_code == ErrorCode.VALIDATION_ERROR
        assert error.filename == "test.xyz"
        assert ".cif" in error.allowed_extensions

    def test_error_code_values(self):
        """Test ErrorCode enum values."""
        assert ErrorCode.VALIDATION_ERROR.value == "VALIDATION_ERROR"
        assert ErrorCode.EXECUTION_ERROR.value == "EXECUTION_ERROR"
        assert ErrorCode.PARSE_ERROR.value == "PARSE_ERROR"
        assert ErrorCode.TIMEOUT_ERROR.value == "TIMEOUT_ERROR"


class TestFileValidation:
    """Test cases for file validation middleware."""

    def test_validate_structure_file_cif(self):
        """Test validation of CIF file."""
        content = b"data_test\n_cell_length_a 10.0"
        validate_structure_file("test.cif", content)  # Should not raise

    def test_validate_structure_file_cssr(self):
        """Test validation of CSSR file."""
        content = b"6.926  6.926  6.41\n90 90 90"
        validate_structure_file("test.cssr", content)  # Should not raise

    def test_validate_structure_file_v1(self):
        """Test validation of V1 file."""
        content = b"V1 file content"
        validate_structure_file("test.v1", content)  # Should not raise

    def test_validate_structure_file_invalid_extension(self):
        """Test rejection of invalid file extension."""
        content = b"some content"
        with pytest.raises(FileValidationError) as exc_info:
            validate_structure_file("test.txt", content)
        assert "Invalid file extension" in str(exc_info.value)
        assert exc_info.value.filename == "test.txt"

    def test_validate_structure_file_empty(self):
        """Test rejection of empty file."""
        with pytest.raises(FileValidationError) as exc_info:
            validate_structure_file("test.cif", b"")
        assert "empty" in str(exc_info.value).lower()

    def test_validate_structure_file_case_insensitive(self):
        """Test that extension validation is case-insensitive."""
        content = b"data_test\n_cell_length_a 10.0"
        validate_structure_file("test.CIF", content)  # Should not raise
        validate_structure_file("test.Cif", content)  # Should not raise

    def test_allowed_extensions_list(self):
        """Test that all expected extensions are allowed."""
        expected = {".cif", ".cssr", ".v1", ".pdb", ".xyz", ".car"}
        assert expected.issubset(set(ALLOWED_EXTENSIONS))


class TestCleanupUtilities:
    """Test cases for cleanup utility functions."""

    @pytest.fixture
    def temp_dir_with_files(self, tmp_path):
        """Create a temporary directory with some files."""
        (tmp_path / "file1.cif").write_text("content1")
        (tmp_path / "file2.res").write_text("content2")
        (tmp_path / "subdir").mkdir()
        (tmp_path / "subdir" / "file3.sa").write_text("content3")
        return tmp_path

    def test_cleanup_temp_directory(self, temp_dir_with_files):
        """Test cleaning up a temporary directory."""
        from app.utils.cleanup import cleanup_temp_directory
        
        cleanup_temp_directory(str(temp_dir_with_files))
        
        # Directory should be empty or not exist
        if temp_dir_with_files.exists():
            contents = list(temp_dir_with_files.iterdir())
            assert len(contents) == 0

    def test_get_cache_storage_stats(self):
        """Test getting cache storage statistics."""
        from app.utils.cleanup import get_cache_storage_stats
        
        stats = get_cache_storage_stats()
        
        assert "temp_files" in stats
        assert "cache_entries" in stats
        assert isinstance(stats["temp_files"], int)

    def test_clear_all_cache(self):
        """Test clearing all cache."""
        from app.utils.cleanup import clear_all_cache
        
        result = clear_all_cache()
        
        assert "cleared" in result or "message" in result


class TestLoggerUtilities:
    """Test cases for logger utilities."""

    def test_logger_exists(self):
        """Test that logger is properly configured."""
        from app.utils.logger import logger
        
        assert logger is not None

    def test_logger_has_handlers(self):
        """Test that logger has output handlers."""
        from app.utils.logger import logger
        
        # Just verify logger can be used without errors
        logger.info("Test log message")


class TestFileUtilities:
    """Test cases for file utility functions."""

    def test_file_utils_exist(self):
        """Test that file utilities module is importable."""
        from app.utils.file import generate_temp_filename
        
        # Test that function exists and is callable
        assert callable(generate_temp_filename)

    def test_generate_temp_filename(self):
        """Test temporary filename generation."""
        from app.utils.file import generate_temp_filename
        
        filename = generate_temp_filename()
        
        assert isinstance(filename, str)
        assert len(filename) > 0
