from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response

# Metrics
REPORT_LATENCY = Histogram('average_report_latency_seconds', 'Report latency seconds', ['report'])
REPORT_CACHE_HIT = Counter('report_cache_hit_total', 'Cache hits for reports', ['report'])
EXPORT_JOB_DURATION = Histogram('export_job_duration_seconds', 'Export job duration seconds')
ROWS_RETURNED = Histogram('rows_returned', 'Rows returned by report', ['report'])


def metrics_endpoint():
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)
