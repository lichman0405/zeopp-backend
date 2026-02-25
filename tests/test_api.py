# API Integration Tests (Windows-friendly, no Zeo++ binary required)
# -*- coding: utf-8 -*-

from app.core.config import settings


class TestSystemEndpoints:
    def test_root_endpoint(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == settings.app_name
        assert data["version"] == settings.version
        assert data["status"] == "ok"

    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == settings.version
        assert "timestamp" in data

    def test_detailed_health_check(self, client):
        response = client.get("/health/detailed")
        assert response.status_code == 200
        data = response.json()
        assert data["version"] == settings.version
        assert data["api_version"] == "v1"
        assert isinstance(data["zeopp_available"], bool)
        assert "uptime_seconds" in data

    def test_version_endpoint(self, client):
        response = client.get("/version")
        assert response.status_code == 200
        data = response.json()
        assert data["version"] == settings.version
        assert data["api_version"] == "v1"


class TestMetricsEndpoints:
    def test_prometheus_metrics(self, client):
        response = client.get("/metrics")
        assert response.status_code == 200
        assert "zeopp_requests_total" in response.text
        assert response.headers["content-type"].startswith("text/plain")

    def test_metrics_summary(self, client):
        response = client.get("/api/v1/metrics/summary")
        assert response.status_code == 200
        data = response.json()
        assert "uptime_seconds" in data
        assert "total_requests" in data
        assert "latency" in data
        assert "requests_by_status" in data


class TestCacheEndpoints:
    def test_cache_stats(self, client):
        response = client.get("/api/v1/cache/stats")
        assert response.status_code == 200
        data = response.json()
        assert "cache" in data
        assert "temp" in data
        assert "cache_enabled" in data
        assert "count" in data["cache"]
        assert "count" in data["temp"]

    def test_cache_cleanup(self, client):
        response = client.post("/api/v1/cache/cleanup")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "removed" in data
        assert "failed" in data

    def test_cache_cleanup_invalid_hours(self, client):
        response = client.post("/api/v1/cache/cleanup?max_age_hours=0")
        assert response.status_code == 422

    def test_cache_clear(self, client):
        response = client.delete("/api/v1/cache/clear")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "entries_removed" in data
        assert "entries_failed" in data


class TestHeaders:
    def test_request_headers(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert "x-request-id" in response.headers
        assert "x-process-time" in response.headers

    def test_rate_limit_headers(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert "x-ratelimit-limit" in response.headers

    def test_cors_preflight(self, client):
        response = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert response.status_code in [200, 405]


class TestValidationAndErrors:
    def test_invalid_file_extension(self, client):
        files = {"structure_file": ("test.txt", b"invalid", "text/plain")}
        response = client.post("/api/v1/pore_diameter", files=files)
        assert response.status_code == 422

    def test_not_found_endpoint(self, client):
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404

    def test_method_not_allowed(self, client):
        response = client.delete("/health")
        assert response.status_code == 405
