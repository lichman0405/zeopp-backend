# Unit Tests for Core Modules
# -*- coding: utf-8 -*-

from io import BytesIO
import os

from starlette.datastructures import UploadFile

import app.utils.cleanup as cleanup_utils
import app.utils.file as file_utils
from app.core.config import Settings
from app.core.exceptions import (
    ErrorCode,
    ZeoppBaseException,
    ZeoppExecutionError,
    ZeoppInvalidFileTypeError,
    ZeoppParsingError,
)
from app.core.middleware import ALLOWED_EXTENSIONS, validate_structure_file
from app.core.runner import ZeoRunner


class TestSettings:
    def test_settings_defaults(self):
        settings = Settings(_env_file=None)
        assert settings.app_name == "Zeo++ Backend API"
        assert settings.version == "0.3.1"
        assert settings.enable_cache is True
        assert settings.cors_origins_list == ["*"]

    def test_settings_from_env(self, monkeypatch):
        monkeypatch.setenv("ENABLE_CACHE", "false")
        monkeypatch.setenv("MAX_UPLOAD_SIZE_MB", "100")
        monkeypatch.setenv("CORS_ORIGINS", "http://a.com,http://b.com")

        settings = Settings(_env_file=None)
        assert settings.enable_cache is False
        assert settings.max_upload_size_mb == 100
        assert settings.cors_origins_list == ["http://a.com", "http://b.com"]


class TestExceptions:
    def test_base_exception_response(self):
        err = ZeoppBaseException("base")
        response = err.to_response("req-1")
        assert response.error_code == ErrorCode.INTERNAL_ERROR.value
        assert response.message == "base"
        assert response.request_id == "req-1"

    def test_execution_exception(self):
        err = ZeoppExecutionError("exec failed", exit_code=1, stderr="boom")
        assert err.error_code == ErrorCode.EXECUTION_FAILED
        assert err.details["exit_code"] == 1
        assert err.details["stderr"] == "boom"

    def test_parsing_exception(self):
        err = ZeoppParsingError("parse failed", output_file="result.res", raw_content="abc")
        assert err.error_code == ErrorCode.PARSING_FAILED
        assert err.output_file == "result.res"

    def test_invalid_file_type_exception(self):
        err = ZeoppInvalidFileTypeError("invalid", filename="x.txt", allowed_types=[".cif"])
        assert err.error_code == ErrorCode.INVALID_FILE_TYPE
        assert err.details["filename"] == "x.txt"


class TestMiddlewareValidation:
    def test_validate_allowed_extensions(self):
        assert validate_structure_file("a.cif") is True
        assert validate_structure_file("a.cssr") is True
        assert validate_structure_file("a.CIF") is True

    def test_validate_disallowed_extension(self):
        assert validate_structure_file("a.txt") is False
        assert validate_structure_file("") is False

    def test_allowed_extensions_contains_expected(self):
        expected = {".cif", ".cssr", ".v1", ".arc", ".xyz", ".pdb", ".cuc"}
        assert expected.issubset(ALLOWED_EXTENSIONS)


class TestFileUtilities:
    def test_save_uploaded_file_sanitizes_filename(self, monkeypatch, tmp_path):
        temp_root = tmp_path / "tmp"
        monkeypatch.setattr(file_utils, "TMP_DIR", temp_root)

        upload = UploadFile(filename="../evil.cif", file=BytesIO(b"test-data"))
        saved_path = file_utils.save_uploaded_file(upload, prefix="unit")

        assert saved_path.exists()
        assert saved_path.name == "evil.cif"
        assert saved_path.parent.parent == temp_root

    def test_compute_cache_key_deterministic(self, monkeypatch, tmp_path):
        temp_root = tmp_path / "tmp"
        monkeypatch.setattr(file_utils, "TMP_DIR", temp_root)

        upload = UploadFile(filename="a.cif", file=BytesIO(b"abc"))
        saved_path = file_utils.save_uploaded_file(upload, prefix="unit")

        args = ["-ha", "-res", "result.res", "a.cif"]
        key1 = file_utils.compute_cache_key(saved_path, args, "x")
        key2 = file_utils.compute_cache_key(saved_path, args, "x")
        assert key1 == key2


class TestCleanupUtilities:
    def test_storage_stats_and_clear_cache(self, monkeypatch, tmp_path):
        temp_root = tmp_path / "tmp"
        cache_root = tmp_path / "cache"
        temp_root.mkdir()
        cache_root.mkdir()

        # Create temp directory/file
        task_dir = temp_root / "task_1"
        task_dir.mkdir()
        (task_dir / "in.cif").write_text("x", encoding="utf-8")

        # Create cache directory/file
        cache_entry = cache_root / "abc123"
        cache_entry.mkdir()
        (cache_entry / "result.res").write_text("res", encoding="utf-8")

        monkeypatch.setattr(cleanup_utils, "TMP_DIR", temp_root)
        monkeypatch.setattr(cleanup_utils, "CACHE_DIR", cache_root)

        temp_stats = cleanup_utils.get_temp_storage_stats()
        cache_stats = cleanup_utils.get_cache_storage_stats()

        assert temp_stats["exists"] is True
        assert temp_stats["count"] == 1
        assert cache_stats["exists"] is True
        assert cache_stats["count"] == 1

        removed, failed = cleanup_utils.clear_all_cache()
        assert removed == 1
        assert failed == 0

    def test_cleanup_old_temp_files(self, monkeypatch, tmp_path):
        temp_root = tmp_path / "tmp"
        temp_root.mkdir()

        old_dir = temp_root / "old_task"
        old_dir.mkdir()
        (old_dir / "file.cif").write_text("x", encoding="utf-8")

        # Set mtime to 2 days ago
        two_days_ago = os.path.getmtime(old_dir) - (48 * 3600)
        os.utime(old_dir, (two_days_ago, two_days_ago))

        monkeypatch.setattr(cleanup_utils, "TMP_DIR", temp_root)

        removed, failed = cleanup_utils.cleanup_old_temp_files(max_age_hours=24)
        assert removed == 1
        assert failed == 0

    def test_cleanup_temp_directory(self, tmp_path):
        target = tmp_path / "task"
        target.mkdir()
        (target / "file.txt").write_text("data", encoding="utf-8")

        assert cleanup_utils.cleanup_temp_directory(target) is True
        assert not target.exists()


class TestRunnerFallback:
    def test_runner_handles_missing_executable(self, tmp_path):
        structure_file = tmp_path / "input.cif"
        structure_file.write_text("data", encoding="utf-8")

        runner = ZeoRunner(zeo_exec_path="definitely_missing_network_binary")
        result = runner.run_command(
            structure_file=structure_file,
            zeo_args=["--help", structure_file.name],
            output_files=["result.res"],
            extra_identifier="unit",
            skip_cache=True,
        )

        assert result["success"] is False
        assert result["exit_code"] != 0
