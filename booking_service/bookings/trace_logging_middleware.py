import logging

logger = logging.getLogger(__name__)


class TraceHeaderLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        logger.info(
            "Incoming trace headers: traceparent=%s tracestate=%s baggage=%s",
            request.headers.get("traceparent"),
            request.headers.get("tracestate"),
            request.headers.get("baggage"),
        )
        return self.get_response(request)
