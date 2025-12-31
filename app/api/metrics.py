# Prometheus Metrics Endpoint
# -*- coding: utf-8 -*-
# Author: Shibo Li
# Date: 2025-12-31

"""
Prometheus metrics collection for Zeo++ API monitoring.
Provides request counts, latency histograms, and system metrics.
"""

import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List
from fastapi import APIRouter, Response

router = APIRouter(tags=["Monitoring"])


@dataclass
class MetricsStore:
    """Simple in-memory metrics store for Prometheus-compatible output."""
    
    # Request counters: {endpoint: {method: {status: count}}}
    request_counts: Dict[str, Dict[str, Dict[int, int]]] = field(
        default_factory=lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    )
    
    # Request latencies: {endpoint: [latencies_in_seconds]}
    request_latencies: Dict[str, List[float]] = field(
        default_factory=lambda: defaultdict(list)
    )
    
    # Error counts by type
    error_counts: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    
    # Active requests
    active_requests: int = 0
    
    # Total requests served
    total_requests: int = 0
    
    # Service start time
    start_time: float = field(default_factory=time.time)
    
    def record_request(
        self, 
        endpoint: str, 
        method: str, 
        status_code: int, 
        latency: float
    ):
        """Record a completed request."""
        self.request_counts[endpoint][method][status_code] += 1
        self.request_latencies[endpoint].append(latency)
        self.total_requests += 1
        
        # Keep only last 1000 latencies per endpoint to prevent memory growth
        if len(self.request_latencies[endpoint]) > 1000:
            self.request_latencies[endpoint] = self.request_latencies[endpoint][-500:]
    
    def record_error(self, error_type: str):
        """Record an error occurrence."""
        self.error_counts[error_type] += 1
    
    def get_uptime(self) -> float:
        """Get service uptime in seconds."""
        return time.time() - self.start_time
    
    def calculate_percentile(self, values: List[float], percentile: float) -> float:
        """Calculate percentile of a list of values."""
        if not values:
            return 0.0
        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile / 100)
        return sorted_values[min(index, len(sorted_values) - 1)]
    
    def to_prometheus_format(self) -> str:
        """Convert metrics to Prometheus text format."""
        lines = []
        
        # Uptime metric
        lines.append("# HELP zeopp_uptime_seconds Service uptime in seconds")
        lines.append("# TYPE zeopp_uptime_seconds gauge")
        lines.append(f"zeopp_uptime_seconds {self.get_uptime():.2f}")
        lines.append("")
        
        # Total requests
        lines.append("# HELP zeopp_requests_total Total number of requests")
        lines.append("# TYPE zeopp_requests_total counter")
        lines.append(f"zeopp_requests_total {self.total_requests}")
        lines.append("")
        
        # Active requests
        lines.append("# HELP zeopp_active_requests Number of currently active requests")
        lines.append("# TYPE zeopp_active_requests gauge")
        lines.append(f"zeopp_active_requests {self.active_requests}")
        lines.append("")
        
        # Request counts by endpoint, method, status
        lines.append("# HELP zeopp_http_requests_total HTTP requests by endpoint, method and status")
        lines.append("# TYPE zeopp_http_requests_total counter")
        for endpoint, methods in self.request_counts.items():
            for method, statuses in methods.items():
                for status, count in statuses.items():
                    # Sanitize endpoint for Prometheus labels
                    safe_endpoint = endpoint.replace("/", "_").strip("_")
                    lines.append(
                        f'zeopp_http_requests_total{{endpoint="{safe_endpoint}",'
                        f'method="{method}",status="{status}"}} {count}'
                    )
        lines.append("")
        
        # Request latency summary
        lines.append("# HELP zeopp_request_duration_seconds Request latency in seconds")
        lines.append("# TYPE zeopp_request_duration_seconds summary")
        for endpoint, latencies in self.request_latencies.items():
            if latencies:
                safe_endpoint = endpoint.replace("/", "_").strip("_")
                p50 = self.calculate_percentile(latencies, 50)
                p90 = self.calculate_percentile(latencies, 90)
                p99 = self.calculate_percentile(latencies, 99)
                count = len(latencies)
                total = sum(latencies)
                
                lines.append(f'zeopp_request_duration_seconds{{endpoint="{safe_endpoint}",quantile="0.5"}} {p50:.4f}')
                lines.append(f'zeopp_request_duration_seconds{{endpoint="{safe_endpoint}",quantile="0.9"}} {p90:.4f}')
                lines.append(f'zeopp_request_duration_seconds{{endpoint="{safe_endpoint}",quantile="0.99"}} {p99:.4f}')
                lines.append(f'zeopp_request_duration_seconds_sum{{endpoint="{safe_endpoint}"}} {total:.4f}')
                lines.append(f'zeopp_request_duration_seconds_count{{endpoint="{safe_endpoint}"}} {count}')
        lines.append("")
        
        # Error counts
        if self.error_counts:
            lines.append("# HELP zeopp_errors_total Errors by type")
            lines.append("# TYPE zeopp_errors_total counter")
            for error_type, count in self.error_counts.items():
                lines.append(f'zeopp_errors_total{{type="{error_type}"}} {count}')
            lines.append("")
        
        return "\n".join(lines)


# Global metrics store instance
metrics_store = MetricsStore()


@router.get("/metrics", response_class=Response, include_in_schema=False)
async def prometheus_metrics():
    """
    Prometheus metrics endpoint.
    Returns metrics in Prometheus text format for scraping.
    """
    content = metrics_store.to_prometheus_format()
    return Response(
        content=content,
        media_type="text/plain; charset=utf-8"
    )


@router.get("/api/v1/metrics/summary")
async def metrics_summary():
    """
    Get a JSON summary of current metrics.
    Useful for dashboards and quick monitoring.
    """
    store = metrics_store
    
    # Calculate aggregate stats
    total_latencies = []
    for latencies in store.request_latencies.values():
        total_latencies.extend(latencies)
    
    avg_latency = sum(total_latencies) / len(total_latencies) if total_latencies else 0
    
    # Count by status code category
    success_count = 0
    client_error_count = 0
    server_error_count = 0
    
    for methods in store.request_counts.values():
        for statuses in methods.values():
            for status, count in statuses.items():
                if 200 <= status < 300:
                    success_count += count
                elif 400 <= status < 500:
                    client_error_count += count
                elif status >= 500:
                    server_error_count += count
    
    return {
        "uptime_seconds": round(store.get_uptime(), 2),
        "total_requests": store.total_requests,
        "active_requests": store.active_requests,
        "requests_by_status": {
            "2xx": success_count,
            "4xx": client_error_count,
            "5xx": server_error_count
        },
        "latency": {
            "avg_ms": round(avg_latency * 1000, 2),
            "p50_ms": round(store.calculate_percentile(total_latencies, 50) * 1000, 2),
            "p90_ms": round(store.calculate_percentile(total_latencies, 90) * 1000, 2),
            "p99_ms": round(store.calculate_percentile(total_latencies, 99) * 1000, 2)
        },
        "errors": dict(store.error_counts)
    }
