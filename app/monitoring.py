from prometheus_client import start_http_server, Counter, Gauge, Histogram
import time

# Initialize metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP Requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP Request Duration',
    ['method', 'endpoint']
)

ARTICLES_PROCESSED = Counter(
    'articles_processed_total',
    'Total articles processed',
    ['source']
)

SCRAPE_DURATION = Histogram(
    'scrape_duration_seconds',
    'Time taken to scrape all sources'
)

DB_OPERATION_DURATION = Histogram(
    'db_operation_duration_seconds',
    'Database operation duration',
    ['operation']
)

def start_monitoring(port=9090):
    """Start Prometheus metrics server"""
    start_http_server(port)
    return True

def record_request_metrics(method, endpoint, status_code, duration):
    """Record HTTP request metrics"""
    REQUEST_COUNT.labels(method, endpoint, status_code).inc()
    REQUEST_DURATION.labels(method, endpoint).observe(duration)

def record_scrape_metrics(source, duration):
    """Record scraping metrics"""
    ARTICLES_PROCESSED.labels(source).inc()
    SCRAPE_DURATION.observe(duration)

def record_db_metrics(operation, duration):
    """Record database operation metrics"""
    DB_OPERATION_DURATION.labels(operation).observe(duration)