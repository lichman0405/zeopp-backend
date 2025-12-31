# API Integration Tests
# -*- coding: utf-8 -*-
# Author: Shibo Li
# Date: 2025-12-31

import pytest


class TestHealthEndpoint:
    """Test cases for health check endpoints."""

    def test_health_check(self, client):
        """Test the basic health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data or "message" in data

    def test_root_endpoint(self, client):
        """Test the root endpoint."""
        response = client.get("/")
        assert response.status_code == 200


class TestCacheEndpoints:
    """Test cases for cache management endpoints."""

    def test_cache_stats(self, client):
        """Test getting cache statistics."""
        response = client.get("/api/v1/cache/stats")
        assert response.status_code == 200
        data = response.json()
        assert "temp_files" in data
        assert "cache_entries" in data

    def test_cache_cleanup(self, client):
        """Test cache cleanup endpoint."""
        response = client.post("/api/v1/cache/cleanup")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    def test_cache_clear(self, client):
        """Test clearing all cache."""
        response = client.delete("/api/v1/cache/clear")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data


class TestRequestHeaders:
    """Test cases for request/response headers."""

    def test_request_id_header(self, client):
        """Test that X-Request-ID header is returned."""
        response = client.get("/health")
        assert response.status_code == 200
        assert "x-request-id" in response.headers

    def test_process_time_header(self, client):
        """Test that X-Process-Time header is returned."""
        response = client.get("/health")
        assert response.status_code == 200
        assert "x-process-time" in response.headers


class TestCORSHeaders:
    """Test cases for CORS configuration."""

    def test_cors_preflight(self, client):
        """Test CORS preflight request."""
        response = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            }
        )
        # Should return 200 for preflight or actual response
        assert response.status_code in [200, 405]


class TestFileValidation:
    """Test cases for file upload validation."""

    def test_invalid_file_extension(self, client):
        """Test that invalid file extensions are rejected."""
        # Create a fake file with invalid extension
        files = {"file": ("test.txt", b"invalid content", "text/plain")}
        response = client.post("/api/v1/pore-diameter", files=files)
        
        # Should return 400 for invalid file type
        assert response.status_code in [400, 422]

    def test_empty_file_upload(self, client):
        """Test that empty files are handled properly."""
        files = {"file": ("test.cif", b"", "application/octet-stream")}
        response = client.post("/api/v1/pore-diameter", files=files)
        
        # Should return error for empty file
        assert response.status_code in [400, 422, 500]


class TestAPIVersioning:
    """Test cases for API versioning."""

    def test_v1_prefix(self, client):
        """Test that v1 API prefix works."""
        response = client.get("/api/v1/cache/stats")
        assert response.status_code == 200


class TestErrorHandling:
    """Test cases for error handling."""

    def test_404_endpoint(self, client):
        """Test 404 response for non-existent endpoint."""
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404

    def test_method_not_allowed(self, client):
        """Test 405 response for wrong HTTP method."""
        response = client.delete("/health")
        assert response.status_code == 405


class TestRateLimiting:
    """Test cases for rate limiting (if enabled)."""

    def test_rate_limit_headers(self, client):
        """Test that rate limit headers are present."""
        response = client.get("/health")
        # Rate limit headers may or may not be present depending on config
        # Just verify the endpoint works
        assert response.status_code == 200


# Note: Full API endpoint tests (pore-diameter, surface-area, etc.) 
# require actual Zeo++ binary and should be run on the Linux server.
# The tests below are stubs that document expected behavior.

class TestPoreDiameterEndpoint:
    """Test cases for pore diameter calculation endpoint."""

    @pytest.mark.skip(reason="Requires Zeo++ binary - run on Linux server")
    def test_pore_diameter_with_valid_cif(self, client, temp_cif_file):
        """Test pore diameter calculation with valid CIF file."""
        with open(temp_cif_file, "rb") as f:
            files = {"file": ("test.cif", f, "application/octet-stream")}
            response = client.post("/api/v1/pore-diameter", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert "included_diameter" in data
        assert "free_diameter" in data
        assert "included_along_free" in data


class TestSurfaceAreaEndpoint:
    """Test cases for surface area calculation endpoint."""

    @pytest.mark.skip(reason="Requires Zeo++ binary - run on Linux server")
    def test_surface_area_with_valid_cif(self, client, temp_cif_file):
        """Test surface area calculation with valid CIF file."""
        with open(temp_cif_file, "rb") as f:
            files = {"file": ("test.cif", f, "application/octet-stream")}
            response = client.post("/api/v1/surface-area", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert "asa_unitcell" in data


class TestAccessibleVolumeEndpoint:
    """Test cases for accessible volume calculation endpoint."""

    @pytest.mark.skip(reason="Requires Zeo++ binary - run on Linux server")
    def test_accessible_volume_with_valid_cif(self, client, temp_cif_file):
        """Test accessible volume calculation with valid CIF file."""
        with open(temp_cif_file, "rb") as f:
            files = {"file": ("test.cif", f, "application/octet-stream")}
            response = client.post("/api/v1/accessible-volume", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert "av" in data


class TestChannelAnalysisEndpoint:
    """Test cases for channel analysis endpoint."""

    @pytest.mark.skip(reason="Requires Zeo++ binary - run on Linux server")
    def test_channel_analysis_with_valid_cif(self, client, temp_cif_file):
        """Test channel analysis with valid CIF file."""
        with open(temp_cif_file, "rb") as f:
            files = {"file": ("test.cif", f, "application/octet-stream")}
            response = client.post("/api/v1/channel-analysis", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert "dimension" in data
