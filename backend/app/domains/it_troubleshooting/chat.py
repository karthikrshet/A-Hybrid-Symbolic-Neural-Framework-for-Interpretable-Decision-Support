"""Conversational lexicon for the IT troubleshooting domain."""

KEYWORDS = [
    "server", "cpu", "memory", "ram", "disk", "api", "latency", "response time", "error rate", "service", "outage",
    "crash", "restart", "down", "slow", "application", "system", "microservice", "kubernetes", "pod", "deployment",
    "unhealthy", "throughput", "it", "troubleshoot", "failure", "monitoring",
]
ALIASES = {
    "cpu_utilization": ["cpu", "cpu utilization", "cpu utilisation", "cpu usage", "processor"],
    "memory_utilization": ["memory", "ram", "memory utilization", "memory utilisation", "memory usage", "heap"],
    "disk_utilization": ["disk", "disk usage", "storage", "disk utilization", "disk utilisation"],
    "response_time_ms": ["response time", "latency", "api response", "response", "taking"],
    "error_rate": ["error rate", "errors", "error", "failure rate", "5xx"],
    "throughput_rps": ["throughput", "rps", "requests per second", "req/s", "traffic"],
    "restarts_last_hour": ["restarts", "restarted", "crashes", "crashed", "restart"],
}
OPTION_ALIASES = {
    "service_status": {
        "Unhealthy": ["unhealthy", "health check failing", "health check failed", "is down", "service down", "not responding"],
        "Degraded": ["degraded", "partially working", "intermittent"],
        "Healthy": ["healthy", "health check passing", "up and running"],
    },
}
PATTERNS: list[tuple[str, list[str]]] = []
KEY_FEATURES = ["cpu_utilization", "memory_utilization", "response_time_ms", "error_rate"]
EXAMPLES = [
    "My service has CPU 95%, memory 92%, API response time 8 seconds, error rate 25% and is unhealthy",
    "Server CPU at 70%, memory 65%, latency 400 ms, 1% errors - anything wrong?",
]
