import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.django import DjangoInstrumentor
try:
    from opentelemetry.instrumentation.djangorestframework import DjangoRestFrameworkInstrumentor
except ImportError:
    DjangoRestFrameworkInstrumentor = None

from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.pymongo import PymongoInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes

# Configure OpenTelemetry
def setup_opentelemetry():
    # Set up resource attributes
    resource = Resource.create({
        ResourceAttributes.SERVICE_NAME: "notification-service",
        ResourceAttributes.SERVICE_VERSION: "1.0.0",
        ResourceAttributes.SERVICE_NAMESPACE: "airlines",
    })

    # Set up tracer provider
    trace.set_tracer_provider(TracerProvider(resource=resource))

    # Set up OTLP exporter
    otlp_endpoint = os.environ.get('OTLP_ENDPOINT', 'http://otel-collector.observability.svc.cluster.local:4318/v1/traces')
    otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint)

    # Add span processor
    span_processor = BatchSpanProcessor(otlp_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)

    # Instrument Django
    DjangoInstrumentor().instrument()
    if DjangoRestFrameworkInstrumentor:
        DjangoRestFrameworkInstrumentor().instrument()

    # Instrument requests
    RequestsInstrumentor().instrument()

    # Instrument pymongo (for MongoDB)
    PymongoInstrumentor().instrument()

setup_opentelemetry()
# Call setup when module is imported